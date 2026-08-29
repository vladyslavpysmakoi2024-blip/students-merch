from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.cart import CartItemCreate
from app.crud import crud_cart

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.get("")
async def get_user_cart(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. Звертаємося до бази через CRUD
    cart_items = await crud_cart.get_cart_items(db, user_id=current_user.id)

    # 2. Формуємо відповідь (мапінг даних)
    return [
        {
            "bin_id": item.Bin.id,
            "product_id": item.Clothing.id,
            "name": item.Clothing.name,
            "price": item.Clothing.price,
            "size": item.Clothing.size,
            "color": item.Clothing.color,
        }
        for item in cart_items
    ]
    # TODO: Створити схему CartItemResponse для response_model=list[CartItemResponse]


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