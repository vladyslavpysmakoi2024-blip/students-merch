from collections.abc import Sequence

import cloudinary.exceptions
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

import app.features.admin.crud as crud_admin
import app.features.clothing.crud as crud_clothing
from app.api.dependencies import get_current_admin, get_db
from app.core.cache import clear_site_cache, clear_user_cache
from app.core.schemas import MessageResponse
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
from app.features.user.router import ALLOWED_AVATAR_TYPES, MAX_AVATAR_SIZE, require_cloudinary

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

    await clear_site_cache("/clothing/simple-list")
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

    await clear_site_cache("/clothing/simple-list")
    for clothing_id in ids:
        await clear_site_cache(f"/clothing/{clothing_id}")
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

    await clear_site_cache("/clothing/simple-list")
    for clothing_id in ids:
        await clear_site_cache(f"/clothing/{clothing_id}")
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

    await clear_site_cache("/clothing/simple-list")
    await clear_site_cache(f"/clothing/{clothing_id}")
    return clothing


@router.post("/clothing/photo")
async def upload_clothing_photo(file: UploadFile = File(...)):  # noqa
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
