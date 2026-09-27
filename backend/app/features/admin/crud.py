from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.admin.schemas import ClothingCreate, PromoCreate
from app.features.cart.models import Cart
from app.features.clothing.models import Clothing
from app.features.favorite.models import Favorite
from app.features.order.models import Order
from app.features.order_content.models import OrderContent
from app.features.promo.models import Promo


async def get_all_clothes(db: AsyncSession) -> Sequence[Clothing]:
    result = await db.execute(select(Clothing).order_by(Clothing.id))
    return result.scalars().all()


async def get_clothes_by_ids(db: AsyncSession, ids: set[int]) -> Sequence[Clothing]:
    result = await db.execute(select(Clothing).where(Clothing.id.in_(ids)).order_by(Clothing.id))
    return result.scalars().all()


async def create_clothes(db: AsyncSession, items: list[ClothingCreate]) -> list[Clothing]:
    clothes = [Clothing(**item.model_dump()) for item in items]
    db.add_all(clothes)
    await db.commit()
    return clothes


async def update_clothes(db: AsyncSession, clothes: Sequence[Clothing], changes: dict) -> Sequence[Clothing]:
    for clothing in clothes:
        for field, value in changes.items():
            setattr(clothing, field, value)

    await db.commit()
    return clothes


async def update_clothing(db: AsyncSession, clothing: Clothing, payload: ClothingCreate) -> Clothing:
    for field, value in payload.model_dump().items():
        setattr(clothing, field, value)

    await db.commit()
    await db.refresh(clothing)
    return clothing


async def get_ordered_clothing_ids(db: AsyncSession, ids: set[int]) -> set[int]:
    result = await db.execute(select(OrderContent.id_clothing).where(OrderContent.id_clothing.in_(ids)).distinct())
    return set(result.scalars().all())


async def delete_clothes(db: AsyncSession, ids: set[int]) -> set[int]:
    result = await db.execute(delete(Favorite).where(Favorite.id_clothing.in_(ids)).returning(Favorite.id_user))
    favorite_user_ids = set(result.scalars().all())
    await db.execute(delete(Cart).where(Cart.id_clothing.in_(ids)))
    await db.execute(delete(Clothing).where(Clothing.id.in_(ids)))
    await db.commit()
    return favorite_user_ids


async def get_all_promos(db: AsyncSession) -> Sequence[Promo]:
    result = await db.execute(select(Promo).order_by(Promo.date_end.desc(), Promo.id))
    return result.scalars().all()


async def get_promo(db: AsyncSession, promo_id: int) -> Promo | None:
    result = await db.execute(select(Promo).where(Promo.id == promo_id))
    return result.scalar_one_or_none()


async def get_promo_by_code(db: AsyncSession, promo: str) -> Promo | None:
    result = await db.execute(select(Promo).where(func.lower(Promo.promo) == promo.lower()))
    return result.scalars().first()


async def create_promo(db: AsyncSession, payload: PromoCreate) -> Promo:
    promo = Promo(**payload.model_dump())
    db.add(promo)
    await db.commit()
    await db.refresh(promo)
    return promo


async def update_promo(db: AsyncSession, promo: Promo, payload: PromoCreate) -> Promo:
    for field, value in payload.model_dump().items():
        setattr(promo, field, value)

    await db.commit()
    await db.refresh(promo)
    return promo


async def delete_promo(db: AsyncSession, promo: Promo) -> None:
    await db.delete(promo)
    await db.commit()


async def get_all_orders(db: AsyncSession) -> Sequence[Order]:
    query = (
        select(Order)
        .options(
            selectinload(Order.status),
            selectinload(Order.user),
            selectinload(Order.order_content).selectinload(OrderContent.clothing),
        )
        .order_by(Order.id.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()
