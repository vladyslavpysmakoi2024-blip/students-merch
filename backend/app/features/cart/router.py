from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.features.user.models import User
from app.features.cart.schemas import CartItemCreate, CartItemResponse, CartItemUpdate
import app.features.cart.crud as crud_cart

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.get("", response_model=list[CartItemResponse])
async def get_user_cart(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. Звертаємося до бази через CRUD
    cart_items = await crud_cart.get_cart_items(db, user_id=current_user.id)

    # 2. Формуємо відповідь (мапінг даних)
    return [
        CartItemResponse(
            id=item.Cart.id,
            product_id=item.Clothing.id,
            name=item.Clothing.name,
            price=item.Clothing.price,
            size=item.Clothing.size,
            color=item.Clothing.color,
        )
        for item in cart_items
    ]

@router.post("")
async def add_to_cart(
        data: CartItemCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    item, is_new = await crud_cart.create_or_update_cart_item(
        db=db,
        user_id=current_user.id,
        clothing_id=data.id_clothing,
        quantity=data.quantity
    )

    if not is_new:
        return {"status": "updated", "new_quantity": item.quantity}

    return {"status": "success", "cart_item_id": item.id}


@router.patch("/{cart_id}")
async def update_cart_item(
        cart_id: int,
        data: CartItemUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    item = await crud_cart.update_cart_item_quantity(
        db=db,
        user_id=current_user.id,
        cart_id=cart_id,
        quantity=data.quantity
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"status": "updated", "new_quantity": item.quantity}


@router.delete("/{cart_id}")
async def remove_cart_item(
        cart_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    deleted = await crud_cart.delete_cart_item(
        db=db,
        user_id=current_user.id,
        cart_id=cart_id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"status": "deleted", "cart_id": cart_id}