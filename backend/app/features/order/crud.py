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
    # Генеруємо поточний час у UTC і прибираємо інформацію про часовий пояс
    current_naive_time = datetime.now(timezone.utc).replace(tzinfo=None)

    new_order = Order(
        price=payload.price,
        id_user=user.id,
        date=current_naive_time,
    )
    db.add(new_order)
    await db.flush()

    for item_id in payload.id_clothing:
        new_order_content = OrderContent(
            id_clothing=item_id, id_order=new_order.id)
        db.add(new_order_content)

    await db.commit()
    return new_order


async def update_order_status(db: AsyncSession, order_id: int, new_status: str) -> bool:
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if order:
        order.status = new_status
        await db.commit()
        return True
    return False


async def update_order_invoice_id(db: AsyncSession, order_id: int, invoice_id: str) -> None:
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if order:
        order.invoice_id = invoice_id
        await db.commit()


async def get_order_by_invoice_id(db: AsyncSession, invoice_id: str) -> Order | None:
    query = select(Order).where(Order.invoice_id == invoice_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
