from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.cart.crud as crud_cart
from app.api.dependencies import get_current_user, get_db
from app.core.colors import color_name
from app.core.schemas import ResponseStatus
from app.features.cart.schemas import (
    CartAddResponse,
    CartDeleteResponse,
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartPackageCreate,
    CartUpdateResponse,
)
from app.features.survey.service import resolve_package_by_id
from app.features.user.models import User

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=list[CartItemResponse])
async def get_user_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Звертаємося до бази через CRUD
    cart_items = await crud_cart.get_cart_items(db, user_id=current_user.id)

    # 2. Формуємо відповідь (мапінг даних)
    return [
        CartItemResponse(
            id=item.Cart.id,
            cart_id=item.Cart.id,
            product_id=item.Clothing.id,
            name=item.Clothing.name or "",
            price=item.Clothing.price,
            size=item.Clothing.size or "",
            color=item.Clothing.color or None,
            color_name=color_name(item.Clothing.color),
            type=item.Clothing.type,
            photo=item.Clothing.photos[0] if (item.Clothing.photos and len(item.Clothing.photos) > 0) else None,
            quantity=getattr(item.Cart, "quantity", 1),
        )
        for item in cart_items
    ]


@router.post("", response_model=CartAddResponse)
async def add_to_cart(
    data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item, is_new = await crud_cart.create_or_update_cart_item(
        db=db,
        user_id=current_user.id,
        clothing_id=data.id_clothing,
        quantity=data.quantity,
    )

    if not is_new:
        return {"status": ResponseStatus.UPDATED, "new_quantity": item.quantity}

    return {"status": ResponseStatus.UPDATED, "cart_item_id": item.id}


@router.post("/package")
async def add_package_to_cart(
    data: CartPackageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import app.features.clothing.crud as crud_clothing

    tshirt_id = data.tshirt_id
    tote_id = data.tote_id

    if (not tshirt_id or not tote_id) and data.package_id:
        resolved = await resolve_package_by_id(db, data.package_id)
        if resolved and isinstance(resolved.get("tshirt"), dict) and isinstance(resolved.get("tote"), dict):
            tshirt_id = resolved["tshirt"].get("id")
            tote_id = resolved["tote"].get("id")

    # Try converting IDs to integer
    try:
        tshirt_id = int(tshirt_id) if tshirt_id is not None else None
        tote_id = int(tote_id) if tote_id is not None else None
    except (ValueError, TypeError):
        tshirt_id = None
        tote_id = None

    # Verify clothing items in DB or fallback to available clothes
    tshirt = await crud_clothing.get_clothing_by_id(db, tshirt_id) if tshirt_id else None
    tote = await crud_clothing.get_clothing_by_id(db, tote_id) if tote_id else None

    if not tshirt or not tote:
        available = await crud_clothing.get_available_clothes(db)
        if available:
            if not tshirt:
                tshirt = available[0]
            if not tote:
                tote = available[min(1, len(available) - 1)]
        else:
            raise HTTPException(status_code=400, detail="No available clothes found in catalog")

    item1, _ = await crud_cart.create_or_update_cart_item(
        db=db,
        user_id=current_user.id,
        clothing_id=tshirt.id,
        quantity=1,
    )
    item2, _ = await crud_cart.create_or_update_cart_item(
        db=db,
        user_id=current_user.id,
        clothing_id=tote.id,
        quantity=1,
    )

    # Lock / confirm the package for the user permanently
    import app.features.survey.crud as crud_survey

    survey = await crud_survey.get_survey_by_user(db, current_user.id)
    if survey and not survey.is_package_confirmed:
        if data.package_id:
            survey.assigned_package_id = data.package_id
        await crud_survey.confirm_package(db, survey)

    return {
        "status": ResponseStatus.UPDATED,
        "message": "Package items added to cart successfully",
        "items": [item1.id, item2.id],
    }


@router.patch("/{cart_id}", response_model=CartUpdateResponse)
async def update_cart_item(
    cart_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await crud_cart.update_cart_item_quantity(
        db=db, user_id=current_user.id, cart_id=cart_id, quantity=data.quantity
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"status": ResponseStatus.UPDATED, "new_quantity": item.quantity}


@router.delete("/{cart_id}", response_model=CartDeleteResponse)
async def remove_cart_item(
    cart_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud_cart.delete_cart_item(db=db, user_id=current_user.id, cart_id=cart_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"status": ResponseStatus.DELETED, "cart_id": cart_id}
