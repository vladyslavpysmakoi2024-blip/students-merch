from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.clothing.crud as crud_clothing
import app.features.order.crud as crud_order
import app.features.promo.crud as crud_promo
from app.api.dependencies import get_current_user, get_db
from app.core.cache import clear_clothing_cache
from app.core.schemas import ResponseStatus
from app.features.order.monobank import create_invoice, is_valid_webhook_signature
from app.features.order.schemas import (
    MonobankWebhook,
    OrderCatalogSchema,
    OrderCreateInfoSchema,
    OrderCreateResponse,
    OrderCreateSchema,
    OrderDetailSchema,
)
from app.features.user.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])

# Статуси рахунку Monobank -> статуси замовлення в нашій базі (CREATED / COMPLETED / FAILED з enum_status)
MONOBANK_STATUS_MAP = {
    "success": "COMPLETED",
    "failure": "FAILED",
    "expired": "FAILED",
    "reversed": "FAILED",
}


async def _calculate_price(db: AsyncSession, counts: Counter[int], promo_code: str | None) -> Decimal:
    clothes = await crud_clothing.get_clothes_by_ids(db, set(counts))

    missing = set(counts) - {clothing.id for clothing in clothes}
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clothing not found: {', '.join(map(str, sorted(missing)))}",
        )

    out_of_stock = [
        clothing.name or f"#{clothing.id}" for clothing in clothes if (clothing.quantity or 0) < counts[clothing.id]
    ]
    if out_of_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостатньо на складі: {', '.join(out_of_stock)}",
        )

    price = sum((clothing.price * counts[clothing.id] for clothing in clothes), Decimal(0))

    if promo_code:
        promo = await crud_promo.get_active_promo(db, promo=promo_code.strip())
        if not promo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Промокод не знайдено або він більше не діє"
            )
        price -= (price * promo.discount_percent / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if price <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сума до оплати має бути більшою за 0")

    return price


# Отримання каталогу замовлень
@router.get("", response_model=list[OrderCatalogSchema])
async def get_orders_catalog(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_order.get_orders_catalog(db, user_id=current_user.id)


# Інформація для нового замовлення (БЕЗПЕЧНО: беремо юзера з токена)
@router.get("/new-info", response_model=OrderCreateInfoSchema)
async def get_info_for_new_order(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderCreateResponse)
async def create_order(
    payload: OrderCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    counts = Counter(payload.id_clothing)
    price = await _calculate_price(db, counts, payload.promo)

    try:
        # 1. Резервуємо товар на складі, щоб його не могли оплатити двічі
        if not await crud_order.reserve_clothes(db, counts):
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Товар щойно закінчився. Онови кошик і спробуй ще раз"
            )

        # 2. Створюємо замовлення
        new_order = await crud_order.create_order(
            db=db, user=current_user, id_clothing=payload.id_clothing, price=price
        )

        # 3. Звертаємось до API Monobank (отримуємо і url, і invoice_id)
        payment_url, invoice_id = await create_invoice(amount=new_order.price, order_id=new_order.id)

        if not payment_url:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail="Не вдалося згенерувати посилання на оплату"
            )

        # 4. Зберігаємо invoice_id і фіксуємо замовлення разом із резервом
        new_order.invoice_id = invoice_id
        await db.commit()

    except httpx.HTTPError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Не вдалося згенерувати посилання на оплату"
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error while saving: {exc!s}") from exc

    await clear_clothing_cache(counts)
    return {"status": ResponseStatus.SUCCESS, "message": "Order created", "payment_url": payment_url}


@router.get("/{order_id}", response_model=OrderDetailSchema)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await crud_order.get_order_detail(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/webhook/monobank")
async def monobank_webhook(
    payload: MonobankWebhook,
    request: Request,
    x_sign: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    print("WEBHOOK RECEIVED:", payload, flush=True)

    if not x_sign:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Sign header")

    try:
        is_valid = await is_valid_webhook_signature(await request.body(), x_sign)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not verify signature"
        ) from exc

    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if not payload.invoiceId:
        return {"status": "ok"}

    # 1. Шукаємо замовлення за invoiceId, який надіслав Монобанк
    order = await crud_order.get_order_by_invoice_id(db, invoice_id=payload.invoiceId)

    if order:
        # 2. Перекладаємо статус Monobank у наш (success -> COMPLETED тощо).
        # Невідомий статус ігноруємо, щоб не записати в базу значення, якого немає в enum
        final_status = MONOBANK_STATUS_MAP.get(payload.status or "")

        # 3. Оновлюємо статус у базі за унікальним id цього замовлення
        if final_status:
            released_ids = await crud_order.update_order_status(db, order=order, new_status=final_status)
            await clear_clothing_cache(released_ids)

    return {"status": "ok"}
