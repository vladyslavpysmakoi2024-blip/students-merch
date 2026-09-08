from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.clothing.models import Clothing


async def get_available_clothes(db: AsyncSession):
    query = select(Clothing).where(Clothing.quantity >= 1)
    result = await db.execute(query)
    return result.scalars().all()


async def get_clothing_by_id(db: AsyncSession, clothing_id: int) -> Clothing | None:
    query = select(Clothing).where(Clothing.id == clothing_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def search_clothing(db: AsyncSession, title: str):
    search_term = title.strip()
    query = select(Clothing).where(
        or_(
            Clothing.name.ilike(f"%{search_term}%"),
            Clothing.type.ilike(f"%{search_term}%"),
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().all()


async def filter_clothing(
    db: AsyncSession,
    clothing_type: str | None,
    color: str | None,
    min_price: float | None,
    max_price: float | None,
    limit: int,
    offset: int,
):
    query = select(Clothing)

    if clothing_type:
        query = query.where(Clothing.type.ilike(clothing_type))
    if color:
        query = query.where(Clothing.color.ilike(color))
    if min_price is not None:
        query = query.where(Clothing.price >= min_price)
    if max_price is not None:
        query = query.where(Clothing.price <= max_price)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


async def get_clothing_by_name(db: AsyncSession, clname: str):
    query = select(Clothing).where(Clothing.name == clname)
    result = await db.execute(query)
    return result.scalars().all()


async def get_clothing_by_name_and_color(db: AsyncSession, clname: str, clcolor: str):
    query = select(Clothing).where(Clothing.name == clname, Clothing.color == clcolor)
    result = await db.execute(query)
    return result.scalars().all()
