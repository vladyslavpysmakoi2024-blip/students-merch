from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.order.crud as crud_order
from app.api.dependencies import get_current_user, get_db
from app.features.order.schemas import (
    OrderCatalogSchema,
    OrderCreateInfoSchema,
    OrderCreateSchema,
    OrderDetailSchema,
)
from app.features.user.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])


# Отримання каталогу замовлень
@router.get("", response_model=list[OrderCatalogSchema])
async def get_orders_catalog(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await crud_order.get_orders_catalog(db, user_id=current_user.id)


# Інформація для нового замовлення (БЕЗПЕЧНО: беремо юзера з токена)
@router.get("/new-info", response_model=OrderCreateInfoSchema)
async def get_info_for_new_order(current_user: User = Depends(get_current_user)):
    # Нам не потрібен запит в БД, бо всі потрібні дані (city, street) вже є в об'єкті current_user
    return current_user


# Створення замовлення (БЕЗПЕЧНО: ігноруємо payload.id_user, використовуємо current_user)
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await crud_order.create_order(db=db, user=current_user, payload=payload)
        return {"status": "success", "message": "Замовлення створено"}
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Помилка при збереженні: {exc!s}"
        ) from exc


@router.get("/{order_id}", response_model=OrderDetailSchema)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await crud_order.get_order_detail(
        db, order_id=order_id, user_id=current_user.id
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
