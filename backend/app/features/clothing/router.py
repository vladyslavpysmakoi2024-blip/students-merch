from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.clothing.crud as crud_clothing
from app.api.dependencies import get_db
from app.features.clothing.schemas import (
    ClothingAdditionalSchema,
    ClothingColoredSchema,
    ClothingDetailSchema,
    ClothingSimpleSchema,
)

router = APIRouter(prefix="/clothing", tags=["Clothing Catalog"])


@router.get("/simple-list", response_model=list[ClothingSimpleSchema])
async def get_clothes_list(db: AsyncSession = Depends(get_db)):
    return await crud_clothing.get_available_clothes(db)


@router.get("/search", response_model=list[ClothingSimpleSchema])
async def search_clothing(title: str, db: AsyncSession = Depends(get_db)):
    return await crud_clothing.search_clothing(db, title=title)


@router.get("/filter", response_model=list[ClothingSimpleSchema])
async def filter_clothing(
    clothing_type: str | None = None,
    color: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await crud_clothing.filter_clothing(
        db=db,
        clothing_type=clothing_type,
        color=color,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/additional", response_model=list[ClothingAdditionalSchema])
async def get_other_colors_sizes(clname: str, db: AsyncSession = Depends(get_db)):
    return await crud_clothing.get_clothing_by_name(db, clname=clname)


@router.get("/colored", response_model=list[ClothingColoredSchema])
async def get_other_sizes_for_colored(
    clname: str, clcolor: str, db: AsyncSession = Depends(get_db)
):
    return await crud_clothing.get_clothing_by_name_and_color(
        db, clname=clname, clcolor=clcolor
    )


@router.get("/clothing/{clothing_id}", response_model=ClothingDetailSchema)
async def get_clothing_detail(clothing_id: int, db: AsyncSession = Depends(get_db)):
    clothing = await crud_clothing.get_clothing_by_id(db, clothing_id=clothing_id)

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing not found")

    return clothing
