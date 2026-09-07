from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.promo.models import Promo


async def get_active_promo(db: AsyncSession, promo: str) -> Promo | None:
    today = datetime.now(tz=timezone.utc).date()
    query = select(Promo).where(
        func.lower(Promo.promo) == promo.lower(), Promo.date_start <= today, Promo.date_end >= today
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
