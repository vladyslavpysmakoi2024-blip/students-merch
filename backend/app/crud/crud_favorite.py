from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite import Favorite

async def get_favorite(db: AsyncSession, user_id: int, clothing_id: int) -> Favorite | None:
    query = select(Favorite).where(
        Favorite.id_user == user_id,
        Favorite.id_clothing == clothing_id
    )
    result = await db.execute(query)
    return result.scalars().first()

async def create_favorite(db: AsyncSession, user_id: int, clothing_id: int) -> Favorite:
    new_favorite = Favorite(
        id_user=user_id,
        id_clothing=clothing_id
    )
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    return new_favorite


async def get_user_favorites(db: AsyncSession, user_id: int):
    query = (
        select(Favorite)
        .options(selectinload(Favorite.clothing))
        .where(Favorite.id_user == user_id)
    )
    result = await db.execute(query)
    return result.scalars().all()