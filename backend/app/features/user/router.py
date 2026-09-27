import cloudinary.exceptions
import cloudinary.uploader
from fastapi import APIRouter, Cookie, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

import app.features.user.crud as crud_user
from app.api.dependencies import get_current_user, get_db
from app.core.cache import invalidate_token_cache
from app.core.config import CLOUDINARY_URL
from app.core.schemas import MessageResponse
from app.core.security import verify_password
from app.features.user.models import User
from app.features.user.schemas import UserAndMessageResponse, UserPasswordUpdate, UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


def avatar_public_id(user_id: int) -> str:
    return f"avatars/user_{user_id}"


def require_cloudinary():
    if not CLOUDINARY_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Робота з фото недоступна: не налаштовано CLOUDINARY_URL",
        )


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


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),  # noqa
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_cloudinary()

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Дозволені лише зображення JPEG, PNG або WebP"
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл порожній")

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="Максимальний розмір фото — 5 МБ")

    try:
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            content,
            public_id=avatar_public_id(current_user.id),
            overwrite=True,
            invalidate=True,
            resource_type="image",
        )
    except cloudinary.exceptions.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Не вдалося завантажити фото. Спробуй ще раз"
        ) from exc

    updated_user = await crud_user.update_avatar(db, db_user=current_user, avatar_url=result["secure_url"])
    return {"avatar_url": updated_user.avatar_url}


@router.delete("/me/avatar")
async def delete_avatar(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_cloudinary()

    if not current_user.avatar_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фото профілю не встановлено")

    try:
        await run_in_threadpool(
            cloudinary.uploader.destroy, avatar_public_id(current_user.id), invalidate=True, resource_type="image"
        )
    except cloudinary.exceptions.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Не вдалося видалити фото. Спробуй ще раз"
        ) from exc

    updated_user = await crud_user.update_avatar(db, db_user=current_user, avatar_url=None)
    return {"avatar_url": updated_user.avatar_url}


@router.patch("/me/password", response_model=MessageResponse)
async def change_password(
    payload: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The current password is incorrect")

    try:
        await crud_user.update_password(db, db_user=current_user, new_password=payload.new_password)
        # Прибираємо закешовану версію цієї сесії — наступний запит
        # перечитає користувача (та зверне увагу на нові дані) замість
        # 15 хв ще жити зі старим кешованим станом.
        if access_token:
            await invalidate_token_cache(access_token)
        return {"message": "Password successfully changed"}
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Server error") from exc
