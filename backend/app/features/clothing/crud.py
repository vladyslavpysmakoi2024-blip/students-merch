from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.colors import color_name
from app.features.clothing.models import Clothing


def one_per_variant(items):
    seen = set()
    unique_items = []
    for item in items:
        key = (item.type, item.name, item.color)
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    return unique_items


async def get_available_clothes(db: AsyncSession):
    query = select(Clothing).where(Clothing.quantity >= 1).order_by(Clothing.id)
    result = await db.execute(query)
    return one_per_variant(result.scalars().all())


async def get_clothing_by_id(db: AsyncSession, clothing_id: int) -> Clothing | None:
    query = select(Clothing).where(Clothing.id == clothing_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def search_clothing(db: AsyncSession, title: str):
    search_term = title.strip()
    query = (
        select(Clothing)
        .where(
            or_(
                Clothing.name.ilike(f"%{search_term}%"),
                Clothing.type.ilike(f"%{search_term}%"),
            )
        )
        .order_by(Clothing.id)
    )
    result = await db.execute(query)
    return one_per_variant(result.scalars().unique().all())


async def filter_clothing(
    db: AsyncSession,
    clothing_type: str | None,
    color: str | None,
    size: str | None,
    min_price: float | None,
    max_price: float | None,
    limit: int,
    offset: int,
):
    query = select(Clothing).order_by(Clothing.id)

    if clothing_type:
        query = query.where(Clothing.type.ilike(clothing_type))
    if size:
        query = query.where(func.lower(Clothing.size) == size.strip().lower())
    if min_price is not None:
        query = query.where(Clothing.price >= min_price)
    if max_price is not None:
        query = query.where(Clothing.price <= max_price)

    result = await db.execute(query)
    items = result.scalars().all()

    if color:
        wanted = color.strip().lower()
        items = [item for item in items if (color_name(item.color) or "").lower() == wanted]

    return one_per_variant(items)[offset : offset + limit]


async def get_clothing_by_name(db: AsyncSession, clname: str):
    query = select(Clothing).where(Clothing.name == clname)
    result = await db.execute(query)
    return result.scalars().all()


async def get_clothing_by_name_and_color(db: AsyncSession, clname: str, clcolor: str):
    query = select(Clothing).where(Clothing.name == clname, Clothing.color == clcolor)
    result = await db.execute(query)
    return result.scalars().all()
