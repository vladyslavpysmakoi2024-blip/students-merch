from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum_models import EnumStatus
from app.features.order.models import Order
from app.features.order.schemas import OrderCreateSchema
from app.features.order_content.models import OrderContent
from app.features.user.models import User


async def get_order_detail(db: AsyncSession, order_id: int, user_id: int) -> Order | None:
    query = (
        select(Order)
        .options(
            selectinload(Order.order_content).selectinload(OrderContent.clothing),
            selectinload(Order.user),
            selectinload(Order.status),
        )
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
            Order.invoice_id,
            func.coalesce(EnumStatus.data, "CREATED").label("status"),
            func.count(OrderContent.id).label("items_count"),
        )
        .outerjoin(EnumStatus, Order.status_id == EnumStatus.id)
        .outerjoin(OrderContent, Order.id == OrderContent.id_order)
        .where(Order.id_user == user_id)
        .group_by(Order.id, Order.price, Order.delivery_company, Order.date, Order.invoice_id, EnumStatus.data)
        .order_by(Order.id.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": row.id,
            "price": str(row.price),
            "delivery_company": row.delivery_company,
            "date": row.date,
            "status": row.status.lower() if row.status else "created",
            "invoice_id": row.invoice_id,
            "items_count": row.items_count,
        }
        for row in rows
    ]


async def get_status_by_name(db: AsyncSession, status_name: str) -> EnumStatus | None:
    norm = status_name.strip().upper()
    if norm in ("SUCCESS", "PAID"):
        norm = "PAID"
    elif norm in ("FAILURE", "FAILED", "EXPIRED", "REVERSED"):
        norm = "FAILED"
    elif norm in ("HOLD", "PROCESSING"):
        norm = "PROCESSING"
    elif norm == "CREATED":
        norm = "CREATED"

    query = select(EnumStatus).where(func.upper(EnumStatus.data) == norm)
    result = await db.execute(query)
    status_obj = result.scalar_one_or_none()
    if not status_obj:
        query_all = select(EnumStatus).limit(1)
        res = await db.execute(query_all)
        status_obj = res.scalar_one_or_none()
    return status_obj


async def create_order(db: AsyncSession, user: User, payload: OrderCreateSchema) -> Order:
    current_naive_time = datetime.now(timezone.utc).replace(tzinfo=None)
    created_status = await get_status_by_name(db, "CREATED")
    status_id = created_status.id if created_status else 1

    new_order = Order(
        price=payload.price,
        id_user=user.id,
        date=current_naive_time,
        status_id=status_id,
    )
    db.add(new_order)
    await db.flush()

    for item_id in payload.id_clothing:
        new_order_content = OrderContent(id_clothing=item_id, id_order=new_order.id)
        db.add(new_order_content)

    await db.commit()
    return new_order


async def update_order_status(db: AsyncSession, order_id: int, new_status: str) -> bool:
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if order:
        status_obj = await get_status_by_name(db, new_status)
        if status_obj:
            order.status_id = status_obj.id
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
