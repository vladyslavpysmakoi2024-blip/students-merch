from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.user.crud as crud_user
from app.api.dependencies import get_current_user, get_db
from app.core.security import verify_password
from app.features.user.models import User
from app.features.user.schemas import UserPasswordUpdate, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "fathers_name": current_user.fathers_name,
        "phone_number": current_user.phone_number,
        "city": current_user.city,
        "street": current_user.street,
        "house_number": current_user.house_number,
    }


@router.patch("/me")
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


@router.patch("/me/password")
async def change_password(
    payload: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поточний пароль невірний")

    try:
        await crud_user.update_password(db, db_user=current_user, new_password=payload.new_password)
        return {"message": "Пароль успішно змінено"}
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Помилка сервера") from exc
