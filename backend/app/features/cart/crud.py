from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.cart.models import Cart
from app.features.clothing.models import Clothing

async def get_cart_items(db: AsyncSession, user_id: int):
    query = (
        select(Cart, Clothing)
        .join(Clothing, Cart.id_clothing == Clothing.id)
        .where(Cart.id_user == user_id)
    )
    result = await db.execute(query)
    # Повертає список кортежів (tuple), де кожен елемент містить (Bin, Clothing)
    return result.all()

async def get_cart_item(db: AsyncSession, user_id: int, clothing_id: int) -> Cart | None:
    query = select(Cart).where(
        Cart.id_user == user_id,
        Cart.id_clothing == clothing_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_or_update_cart_item(db: AsyncSession, user_id: int, clothing_id: int, quantity: int):
    existing_item = await get_cart_item(db, user_id, clothing_id)

    # Якщо товар вже є в кошику, просто збільшуємо кількість
    if existing_item:
        existing_item.quantity += quantity
        await db.commit()
        await db.refresh(existing_item)
        return existing_item, False  # False означає, що запис оновлено

    # Якщо товару немає, створюємо новий
    new_item = Cart(
        id_user=user_id,
        id_clothing=clothing_id,
        quantity=quantity
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item, True  # True означає, що запис створено


async def get_cart_item_by_id(db: AsyncSession, user_id: int, cart_id: int) -> Cart | None:
    query = select(Cart).where(Cart.id == cart_id, Cart.id_user == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_cart_item_quantity(db: AsyncSession, user_id: int, cart_id: int, quantity: int) -> Cart | None:
    item = await get_cart_item_by_id(db, user_id=user_id, cart_id=cart_id)
    if not item:
        return None

    item.quantity = quantity
    await db.commit()
    await db.refresh(item)
    return item


async def delete_cart_item(db: AsyncSession, user_id: int, cart_id: int) -> bool:
    item = await get_cart_item_by_id(db, user_id=user_id, cart_id=cart_id)
    if not item:
        return False

    await db.delete(item)
    await db.commit()
    return True