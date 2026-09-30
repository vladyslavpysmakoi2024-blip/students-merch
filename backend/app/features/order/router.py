from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.order.crud as crud_order
from app.api.dependencies import get_current_user, get_db
from app.core.schemas import ResponseStatus
from app.features.order.monobank import create_invoice, get_invoice_status
from app.features.order.schemas import (
    MonobankWebhook,
    OrderCatalogSchema,
    OrderCreateInfoSchema,
    OrderCreateResponse,
    OrderCreateSchema,
    OrderDetailSchema,
    OrderReceiptSchema,
    ReceiptCustomerSchema,
    ReceiptItemSchema,
)
from app.features.user.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])

# Статуси рахунку Monobank -> статуси замовлення в нашій базі (created / processing / paid / failure)
MONOBANK_STATUS_MAP = {
    "created": "created",
    "processing": "processing",
    "hold": "processing",
    "success": "paid",
    "failure": "failure",
    "expired": "failure",
    "reversed": "failure",
}


# Отримання каталогу замовлень
@router.get("", response_model=list[OrderCatalogSchema])
async def get_orders_catalog(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    orders = await crud_order.get_orders_catalog(db, user_id=current_user.id)

    # Синхронізуємо статуси неоплачених замовлень із Monobank API
    for order in orders:
        if order.get("status") not in ("paid", "completed", "failed") and order.get("invoice_id"):
            mono_status = await get_invoice_status(order["invoice_id"])
            if mono_status:
                raw_status = (mono_status.get("status") or "").lower()
                final_status = MONOBANK_STATUS_MAP.get(raw_status)
                if final_status and final_status != order.get("status"):
                    await crud_order.update_order_status(db, order_id=order["id"], new_status=final_status)
                    order["status"] = final_status

    return orders


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
    try:
        # 1. Створюємо замовлення
        new_order = await crud_order.create_order(db=db, user=current_user, payload=payload)

        # 2. Звертаємось до API Monobank (отримуємо і url, і invoice_id)
        payment_url, invoice_id = await create_invoice(amount=float(new_order.price), order_id=new_order.id)

        if not payment_url:
            raise HTTPException(status_code=500, detail="Не вдалося згенерувати посилання на оплату")

        # 3. Зберігаємо invoice_id у щойно створене замовлення
        await crud_order.update_order_invoice_id(db, order_id=new_order.id, invoice_id=invoice_id)

        return {"status": ResponseStatus.SUCCESS, "message": "Order created", "payment_url": payment_url}

    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error while saving: {exc!s}") from exc


@router.get("/{order_id}", response_model=OrderDetailSchema)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await crud_order.get_order_detail(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_status = order.status.data.lower() if hasattr(order.status, "data") else str(order.status).lower()
    if order_status not in ("paid", "completed", "failed") and order.invoice_id:
        mono_status = await get_invoice_status(order.invoice_id)
        if mono_status:
            raw_status = (mono_status.get("status") or "").lower()
            final_status = MONOBANK_STATUS_MAP.get(raw_status)
            if final_status and final_status != order_status:
                await crud_order.update_order_status(db, order_id=order.id, new_status=final_status)
                order = await crud_order.get_order_detail(db, order_id=order_id, user_id=current_user.id)
    return order


@router.get("/{order_id}/receipt", response_model=OrderReceiptSchema)
async def get_order_receipt(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await crud_order.get_order_detail(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")

    order_status = order.status.data.lower() if hasattr(order.status, "data") else str(order.status).lower()

    # Перевірка на оплату (якщо ще не оновлено в БД, спробуємо опитати Монобанк наживо)
    if order_status not in ("paid", "success") and order.invoice_id:
        mono_status = await get_invoice_status(order.invoice_id)
        if mono_status and mono_status.get("status") == "success":
            await crud_order.update_order_status(db, order_id=order.id, new_status="paid")
            order_status = "paid"

    if order_status not in ("paid", "success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Чек та квитанція доступні виключно для оплачених замовлень",
        )

    # Дані квитанції Monobank
    mono_info = await get_invoice_status(order.invoice_id) if order.invoice_id else None
    monobank_receipt_id = mono_info.get("receipt_id") if mono_info else None
    monobank_receipt_url = mono_info.get("receipt_url") if mono_info else None

    customer_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or "Клієнт"
    customer = ReceiptCustomerSchema(
        name=customer_name,
        email=current_user.email,
        phone=current_user.phone_number,
        city=current_user.city,
        street=current_user.street,
        house_number=current_user.house_number,
    )

    items: list[ReceiptItemSchema] = []
    subtotal = 0.0
    for content in order.order_content:
        cl = content.clothing
        if cl:
            price_val = float(cl.price)
            photo = cl.photos[0] if (cl.photos and len(cl.photos) > 0) else None
            items.append(
                ReceiptItemSchema(
                    id=cl.id,
                    name=cl.name or "Товар",
                    type=cl.type,
                    color=cl.color,
                    size=cl.size,
                    price=price_val,
                    quantity=1,
                    total=price_val,
                    photo=photo,
                )
            )
            subtotal += price_val

    total_amount = float(order.price) if order.price else subtotal

    return OrderReceiptSchema(
        order_id=order.id,
        receipt_number=f"CHK-{order.id:06d}",
        created_at=order.date,
        status="ОПЛАЧЕНО",
        payment_method="Monobank Онлайн",
        invoice_id=order.invoice_id,
        monobank_receipt_id=monobank_receipt_id,
        monobank_receipt_url=monobank_receipt_url,
        customer=customer,
        delivery_company=order.delivery_company,
        delivery_type=order.delivery_type,
        postal_number=order.postal_number,
        items=items,
        subtotal=subtotal,
        total_amount=total_amount,
        currency="UAH",
    )


@router.post("/webhook/monobank")
async def monobank_webhook(payload: MonobankWebhook, db: AsyncSession = Depends(get_db)):
    print("WEBHOOK RECEIVED:", payload, flush=True)

    if not payload.invoiceId:
        return {"status": "ok"}

    # 1. Шукаємо замовлення за invoiceId, який надіслав Монобанк
    order = await crud_order.get_order_by_invoice_id(db, invoice_id=payload.invoiceId)

    if order:
        # 2. Перекладаємо статус Monobank у наш (success -> paid тощо).
        # Невідомий статус ігноруємо, щоб не записати в базу значення, якого немає в enum
        final_status = MONOBANK_STATUS_MAP.get(payload.status or "")

        # 3. Оновлюємо статус у базі за унікальним id цього замовлення
        if final_status:
            await crud_order.update_order_status(db, order_id=order.id, new_status=final_status)

    return {"status": "ok"}
