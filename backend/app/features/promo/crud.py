from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.promo.models import Promo


async def get_active_promo(db: AsyncSession, promo: str) -> Promo | None:
    today = date.today()
    query = select(Promo).where(
        func.lower(Promo.promo) == promo.lower(),
        Promo.date_start <= today,
        Promo.date_end >= today
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
