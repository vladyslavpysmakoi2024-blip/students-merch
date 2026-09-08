from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.order.models import Order
from app.features.order.schemas import OrderCreateSchema
from app.features.order_content.models import OrderContent
from app.features.user.models import User


async def get_order_detail(db: AsyncSession, order_id: int, user_id: int) -> Order | None:
    query = (
        select(Order)
        .options(selectinload(Order.order_content).selectinload(OrderContent.clothing))
        .where(Order.id == order_id, Order.id_user == user_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_orders_catalog(db: AsyncSession, user_id: int) -> list[dict]:
    query = (
        select(
            Order.id,
            Order.price,  # <--- Замінили cost на price
            Order.delivery_company,
            Order.date,
            func.count(OrderContent.id).label("items_count"),
        )
        .outerjoin(OrderContent, Order.id == OrderContent.id_order)
        .group_by(Order.id)
        .where(Order.id_user == user_id)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": row.id,
            "price": str(row.price),
            "delivery_company": row.delivery_company,
            "date": row.date,
            "items_count": row.items_count,
        }
        for row in rows
    ]


async def create_order(db: AsyncSession, user: User, payload: OrderCreateSchema) -> Order:
    # Оновлюємо дані користувача
    user.city = payload.city
    user.street = payload.street
    user.house_number = payload.house_number

    # Створюємо замовлення
    new_order = Order(
        price=payload.price,
        delivery_company=payload.delivery_company,
        delivery_type=payload.delivery_type,
        postal_number=payload.postal_number,
        id_user=user.id,
        date=datetime.now(timezone.utc),
    )
    db.add(new_order)
    await db.flush()

    # Додаємо товари до замовлення
    for item_id in payload.id_clothing:
        new_order_content = OrderContent(id_clothing=item_id, id_order=new_order.id)
        db.add(new_order_content)

    await db.commit()
    return new_order
