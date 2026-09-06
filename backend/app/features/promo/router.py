from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.features.promo.schemas import PromoApply, PromoResponse
from app.features.user.models import User
import app.features.promo.crud as crud_promo

router = APIRouter(prefix="/promo", tags=["Promo"])


@router.post("/apply", response_model=PromoResponse)
async def apply_promo(
    data: PromoApply, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    code = data.promo.strip()
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Промокод не вказано")

    promo = await crud_promo.get_active_promo(db, promo=code)
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промокод не знайдено або він більше не діє")

    return promo
