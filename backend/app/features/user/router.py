import cloudinary.exceptions
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_db, get_current_user
from app.core.config import CLOUDINARY_URL
from app.core.security import verify_password
import app.features.user.crud as crud_user

from app.features.user.schemas import UserPasswordUpdate, UserUpdate
from app.features.user.models import User

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


def avatar_public_id(user_id: int) -> str:
    return f"avatars/user_{user_id}"


def require_cloudinary():
    if not CLOUDINARY_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Робота з фото недоступна: не налаштовано CLOUDINARY_URL"
        )


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
        "avatar_url": current_user.avatar_url,
    }


@router.patch("/me")
async def update_current_user(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Перевіряємо, чи є взагалі що оновлювати
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data to update is not provided"
        )

    # 2. Викликаємо ізольовану логіку бази даних
    try:
        updated_user = await crud_user.update_user(db=db, db_user=current_user, user_in=payload)
        return {"message": "User updated successfully", "user": updated_user}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while updating user"
        )


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_cloudinary()

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дозволені лише зображення JPEG, PNG або WebP"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл порожній"
        )

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Максимальний розмір фото — 5 МБ"
        )

    try:
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            content,
            public_id=avatar_public_id(current_user.id),
            overwrite=True,
            invalidate=True,
            resource_type="image"
        )
    except cloudinary.exceptions.Error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не вдалося завантажити фото. Спробуй ще раз"
        )

    updated_user = await crud_user.update_avatar(
        db, db_user=current_user, avatar_url=result["secure_url"]
    )
    return {"avatar_url": updated_user.avatar_url}


@router.delete("/me/avatar")
async def delete_avatar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_cloudinary()

    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фото профілю не встановлено"
        )

    try:
        await run_in_threadpool(
            cloudinary.uploader.destroy,
            avatar_public_id(current_user.id),
            invalidate=True,
            resource_type="image"
        )
    except cloudinary.exceptions.Error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не вдалося видалити фото. Спробуй ще раз"
        )

    updated_user = await crud_user.update_avatar(
        db, db_user=current_user, avatar_url=None
    )
    return {"avatar_url": updated_user.avatar_url}


@router.patch("/me/password")
async def change_password(
    payload: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поточний пароль невірний"
        )

    try:
        await crud_user.update_password(db, db_user=current_user, new_password=payload.new_password)
        return {"message": "Пароль успішно змінено"}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Помилка сервера")