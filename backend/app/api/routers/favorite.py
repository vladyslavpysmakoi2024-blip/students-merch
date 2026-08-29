from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.schemas.cart import FavoriteCreate, FavoriteSchema
from app.models.user import User
from app.crud import crud_favorite


router = APIRouter(prefix="/favorite",
                   tags=["Favorites"])

@router.get("", response_model=list[FavoriteSchema])
async def get_favorites(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # Звертаємося до бази через CRUD
    favorites = await crud_favorite.get_user_favorites(db, user_id=current_user.id)
    return list(favorites)


@router.post("")
async def add_to_favorites(
        data: FavoriteCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    existing_favorite = await crud_favorite.get_favorite(
        db=db,
        user_id=current_user.id,
        clothing_id=data.id_clothing
    )

    if existing_favorite:
        return {"message": "Товар вже в обраному"}

    new_favorite = await crud_favorite.create_favorite(
        db=db,
        user_id=current_user.id,
        clothing_id=data.id_clothing
    )

    return {"status": "success", "favorite_id": new_favorite.id}