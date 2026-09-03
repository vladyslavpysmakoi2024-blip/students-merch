from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.favorite.models import Favorite


async def get_favorite(db: AsyncSession, user_id: int, clothing_id: int) -> Favorite | None:
    query = select(Favorite).where(Favorite.id_user == user_id, Favorite.id_clothing == clothing_id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_favorite(db: AsyncSession, user_id: int, clothing_id: int) -> Favorite:
    new_favorite = Favorite(id_user=user_id, id_clothing=clothing_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    return new_favorite


async def get_user_favorites(db: AsyncSession, user_id: int):
    query = select(Favorite).options(selectinload(Favorite.clothing)).where(Favorite.id_user == user_id)
    result = await db.execute(query)
    return result.scalars().all()


async def delete_favorite(db: AsyncSession, user_id: int, clothing_id: int) -> bool:
    favorite = await get_favorite(db=db, user_id=user_id, clothing_id=clothing_id)

    if not favorite:
        return False

    await db.delete(favorite)
    await db.commit()

    return True
