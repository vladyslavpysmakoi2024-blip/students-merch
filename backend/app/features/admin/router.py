from collections.abc import Sequence

import cloudinary.exceptions
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

import app.features.admin.crud as crud_admin
import app.features.clothing.crud as crud_clothing
import app.features.user.crud as crud_user
from app.api.dependencies import get_current_admin, get_db
from app.core.cache import clear_site_cache_prefix, clear_user_cache, invalidate_user_cache
from app.core.config import CLOUDINARY_URL
from app.core.rate_limit import rate_limit
from app.core.schemas import MessageResponse
from app.core.utils import require_cloudinary, validate_image_file
from app.features.admin.schemas import (
    ClothingBulkCreate,
    ClothingBulkUpdate,
    ClothingCreate,
    ClothingIds,
    OrderAdminSchema,
    PromoAdminSchema,
    PromoCreate,
)
from app.features.clothing.models import Clothing
from app.features.clothing.schemas import ClothingDetailSchema
from app.features.user.models import User

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

PROMO_EXISTS_DETAIL = "Такий промокод уже існує"


async def get_clothes_or_404(db: AsyncSession, ids: set[int]) -> Sequence[Clothing]:
    clothes = await crud_admin.get_clothes_by_ids(db, ids)
    missing = ids - {clothing.id for clothing in clothes}
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clothing not found: {', '.join(map(str, sorted(missing)))}",
        )
    return clothes


@router.get("/clothing", response_model=list[ClothingDetailSchema])
async def get_clothes(db: AsyncSession = Depends(get_db)):
    return await crud_admin.get_all_clothes(db)


@router.post("/clothing/bulk", status_code=status.HTTP_201_CREATED, response_model=list[ClothingDetailSchema])
async def create_clothes(payload: ClothingBulkCreate, db: AsyncSession = Depends(get_db)):
    try:
        clothes = await crud_admin.create_clothes(db, payload.items)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error while saving clothing") from exc

    await clear_site_cache_prefix("/clothing")
    return clothes


@router.patch("/clothing/bulk", response_model=list[ClothingDetailSchema])
async def update_clothes(payload: ClothingBulkUpdate, db: AsyncSession = Depends(get_db)):
    changes = payload.model_dump(exclude_unset=True, exclude={"ids"})
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data to update is not provided")

    ids = set(payload.ids)
    clothes = await get_clothes_or_404(db, ids)

    try:
        clothes = await crud_admin.update_clothes(db, clothes, changes)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error while saving clothing") from exc

    await clear_site_cache_prefix("/clothing")
    return clothes


@router.post("/clothing/bulk-delete", response_model=MessageResponse)
async def delete_clothes(payload: ClothingIds, db: AsyncSession = Depends(get_db)):
    ids = set(payload.ids)
    await get_clothes_or_404(db, ids)

    ordered = await crud_admin.get_ordered_clothing_ids(db, ids)
    if ordered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Товари {', '.join(f'#{clothing_id}' for clothing_id in sorted(ordered))} є в замовленнях, "
                "їх не можна видалити. Постав кількість 0, щоб прибрати їх із сайту"
            ),
        )

    try:
        favorite_user_ids = await crud_admin.delete_clothes(db, ids)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Товар щойно додали в замовлення, його не можна видалити"
        ) from exc

    await clear_site_cache_prefix("/clothing")
    for user_id in favorite_user_ids:
        await clear_user_cache(func_name="get_favorites", user_id=user_id)
    return {"message": "Clothing deleted"}


@router.put("/clothing/{clothing_id}", response_model=ClothingDetailSchema)
async def update_clothing(clothing_id: int, payload: ClothingCreate, db: AsyncSession = Depends(get_db)):
    clothing = await crud_clothing.get_clothing_by_id(db, clothing_id=clothing_id)
    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing not found")

    try:
        clothing = await crud_admin.update_clothing(db, clothing, payload)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error while saving clothing") from exc

    await clear_site_cache_prefix("/clothing")
    return clothing


@router.post("/clothing/photo", dependencies=[Depends(rate_limit("upload", 10, 60, per_user=True))])
async def upload_clothing_photo(file: UploadFile = File(...)):  # noqa
    require_cloudinary(CLOUDINARY_URL)
    content = await validate_image_file(file)

    try:
        result = await run_in_threadpool(cloudinary.uploader.upload, content, folder="clothing", resource_type="image")
    except cloudinary.exceptions.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Не вдалося завантажити фото. Спробуй ще раз"
        ) from exc

    return {"url": result["secure_url"]}


@router.get("/promo", response_model=list[PromoAdminSchema])
async def get_promos(db: AsyncSession = Depends(get_db)):
    return await crud_admin.get_all_promos(db)


@router.post("/promo", status_code=status.HTTP_201_CREATED, response_model=PromoAdminSchema)
async def create_promo(payload: PromoCreate, db: AsyncSession = Depends(get_db)):
    if await crud_admin.get_promo_by_code(db, promo=payload.promo):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=PROMO_EXISTS_DETAIL)

    try:
        return await crud_admin.create_promo(db, payload)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=PROMO_EXISTS_DETAIL) from exc


@router.put("/promo/{promo_id}", response_model=PromoAdminSchema)
async def update_promo(promo_id: int, payload: PromoCreate, db: AsyncSession = Depends(get_db)):
    promo = await crud_admin.get_promo(db, promo_id=promo_id)
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promo not found")

    duplicate = await crud_admin.get_promo_by_code(db, promo=payload.promo)
    if duplicate and duplicate.id != promo.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=PROMO_EXISTS_DETAIL)

    try:
        return await crud_admin.update_promo(db, promo, payload)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=PROMO_EXISTS_DETAIL) from exc


@router.delete("/promo/{promo_id}", response_model=MessageResponse)
async def delete_promo(promo_id: int, db: AsyncSession = Depends(get_db)):
    promo = await crud_admin.get_promo(db, promo_id=promo_id)
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promo not found")

    await crud_admin.delete_promo(db, promo)
    return {"message": "Promo deleted"}


@router.get("/orders", response_model=list[OrderAdminSchema])
async def get_orders(db: AsyncSession = Depends(get_db)):
    return await crud_admin.get_all_orders(db)


async def _set_user_banned(db: AsyncSession, user_id: int, current_admin: User, banned: bool) -> None:
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if banned and (user.id == current_admin.id or user.is_admin):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban an administrator")

    await crud_user.set_banned(db, user, banned)
    # Інакше закешований користувач ще до 15 хв проходив би get_current_user
    await invalidate_user_cache(user_id)


@router.post("/users/{user_id}/ban", response_model=MessageResponse)
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    await _set_user_banned(db, user_id, current_admin, banned=True)
    return {"message": "User banned"}


@router.post("/users/{user_id}/unban", response_model=MessageResponse)
async def unban_user(
    user_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)
):
    await _set_user_banned(db, user_id, current_admin, banned=False)
    return {"message": "User unbanned"}
