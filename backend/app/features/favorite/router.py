from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.favorite.crud as crud_favorite
from app.api.dependencies import get_current_user, get_db
from app.core.schemas import ResponseStatus
from app.features.favorite.schemas import (
    FavoriteAddResponse,
    FavoriteCreate,
    FavoriteDeleteResponse,
    FavoriteSchema,
)
from app.features.user.models import User

router = APIRouter(prefix="/favorite", tags=["Favorites"])


@router.get("", response_model=list[FavoriteSchema])
async def get_favorites(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    favorites = await crud_favorite.get_user_favorites(db, user_id=current_user.id)

    return favorites


@router.post("", response_model=FavoriteAddResponse)
async def add_to_favorites(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing_favorite = await crud_favorite.get_favorite(db=db, user_id=current_user.id, clothing_id=data.id_clothing)

    if existing_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The item is already in your favorites")
    new_favorite = await crud_favorite.create_favorite(db=db, user_id=current_user.id, clothing_id=data.id_clothing)

    return {"status": ResponseStatus.SUCCESS, "favorite_id": new_favorite.id}


@router.delete("/{clothing_id}", response_model=FavoriteDeleteResponse)
async def delete_from_favorites(
    clothing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud_favorite.delete_favorite(db=db, user_id=current_user.id, clothing_id=clothing_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found in favorites")

    return {"status": ResponseStatus.SUCCESS, "message": "Item removed from favorites"}
