from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.order.crud as crud_order
from app.api.dependencies import get_current_user, get_db
from app.core.schemas import ResponseStatus
from app.features.order.monobank import create_invoice
from app.features.order.schemas import (
    OrderCatalogSchema,
    OrderCreateInfoSchema,
    OrderCreateResponse,
    OrderCreateSchema,
    OrderDetailSchema, MonobankWebhook
)
from app.features.user.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])


# Отримання каталогу замовлень
@router.get("", response_model=list[OrderCatalogSchema])
async def get_orders_catalog(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_order.get_orders_catalog(db, user_id=current_user.id)


# Інформація для нового замовлення (БЕЗПЕЧНО: беремо юзера з токена)
@router.get("/new-info", response_model=OrderCreateInfoSchema)
async def get_info_for_new_order(current_user: User = Depends(get_current_user)):
    # Нам не потрібен запит в БД, бо всі потрібні дані (city, street) вже є в об'єкті current_user
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
            raise HTTPException(
                status_code=500, detail="Не вдалося згенерувати посилання на оплату")

        # 3. Зберігаємо invoice_id у щойно створене замовлення (ДОДАНО AWAIT)
        await crud_order.update_order_invoice_id(db, order_id=new_order.id, invoice_id=invoice_id)

        return {"status": ResponseStatus.SUCCESS, "message": "Order created", "payment_url": payment_url}

    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error while saving: {exc!s}") from exc


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
    db: AsyncSession = Depends(get_db)
):
    print("WEBHOOK RECEIVED:", payload, flush=True)

    if not payload.invoiceId:
        return {"status": "ok"}

    # 1. Шукаємо замовлення за invoiceId, який надіслав Монобанк
    order = await crud_order.get_order_by_invoice_id(db, invoice_id=payload.invoiceId)

    if order:
        # 2. Якщо статус success, перетворюємо його на paid
        final_status = "paid" if payload.status == "success" else payload.status

        # 3. Оновлюємо статус у базі за унікальним id цього замовлення
        await crud_order.update_order_status(db, order_id=order.id, new_status=final_status)

    return {"status": "ok"}
