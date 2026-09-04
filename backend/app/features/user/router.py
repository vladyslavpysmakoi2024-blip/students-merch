from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.user.crud as crud_user
from app.api.dependencies import get_current_user, get_db
from app.core.schemas import MessageResponse
from app.core.security import verify_password
from app.features.user.models import User
from app.features.user.schemas import UserAndMessageResponse, UserPasswordUpdate, UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_user(current_user: User = Depends(get_current_user)):
    # Завдяки from_attributes=True у схемі UserResponse,
    # FastAPI сам дістане всі необхідні поля (адресу, ім'я тощо) з об'єкта SQLAlchemy.
    return current_user


@router.patch("/me", response_model=UserAndMessageResponse)
async def update_current_user(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Перевіряємо, чи є взагалі що оновлювати
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data to update is not provided",
        )

    # 2. Викликаємо ізольовану логіку бази даних
    try:
        updated_user = await crud_user.update_user(db=db, db_user=current_user, user_in=payload)
        return {"message": "User updated successfully", "user": updated_user}
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while updating user",
        ) from exc


@router.patch("/me/password", response_model=MessageResponse)
async def change_password(
    payload: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The current password is incorrect")

    try:
        await crud_user.update_password(db, db_user=current_user, new_password=payload.new_password)
        return {"message": "Password successfully changed"}
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Server error") from exc
