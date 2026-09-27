from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum_models import EnumStatus
from app.features.clothing.models import Clothing
from app.features.order.models import Order
from app.features.order_content.models import OrderContent
from app.features.user.models import User


def status_id_query(status: str):
    return select(EnumStatus.id).where(EnumStatus.data == status).scalar_subquery()


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
            Order.price,
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


async def create_order(db: AsyncSession, user: User, id_clothing: list[int], price: Decimal) -> Order:
    current_naive_time = datetime.now(timezone.utc).replace(tzinfo=None)

    new_order = Order(
        price=price,
        id_user=user.id,
        date=current_naive_time,
        status_id=status_id_query("CREATED"),
    )
    db.add(new_order)
    await db.flush()

    for item_id in id_clothing:
        new_order_content = OrderContent(id_clothing=item_id, id_order=new_order.id)
        db.add(new_order_content)

    await db.flush()
    return new_order


async def reserve_clothes(db: AsyncSession, counts: dict[int, int]) -> bool:
    for clothing_id in sorted(counts):
        result = await db.execute(
            update(Clothing)
            .where(Clothing.id == clothing_id, Clothing.quantity >= counts[clothing_id])
            .values(quantity=Clothing.quantity - counts[clothing_id])
        )
        if result.rowcount == 0:
            return False
    return True


async def release_clothes(db: AsyncSession, order_id: int) -> list[int]:
    result = await db.execute(
        select(OrderContent.id_clothing, func.sum(OrderContent.quantity))
        .where(OrderContent.id_order == order_id, OrderContent.id_clothing.is_not(None))
        .group_by(OrderContent.id_clothing)
        .order_by(OrderContent.id_clothing)
    )
    rows = result.all()
    for clothing_id, count in rows:
        await db.execute(
            update(Clothing)
            .where(Clothing.id == clothing_id)
            .values(quantity=func.coalesce(Clothing.quantity, 0) + count)
        )
    return [clothing_id for clothing_id, _ in rows]


async def update_order_status(db: AsyncSession, order: Order, new_status: str) -> list[int]:
    current_status = (await db.execute(select(EnumStatus.data).where(EnumStatus.id == order.status_id))).scalar_one()
    if current_status in (new_status, "FAILED"):
        return []

    released_ids = await release_clothes(db, order.id) if new_status == "FAILED" else []
    order.status_id = status_id_query(new_status)
    await db.commit()
    return released_ids


async def get_order_by_invoice_id(db: AsyncSession, invoice_id: str) -> Order | None:
    query = select(Order).where(Order.invoice_id == invoice_id).with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()
