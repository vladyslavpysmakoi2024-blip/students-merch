import os
from pathlib import Path
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from jose import JWTError,jwt
from starlette.requests import Request
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from sqlalchemy import select, or_, and_, func
from sqlalchemy import update
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime
from typing import List, Optional
from .database import get_db, hash_password, verify_password, create_access_token, create_refresh_token,ACCESS_TOKEN_EXPIRE_IN_MINUTES, JWT_SECRET_KEY
from .dependency import get_current_user
from .models.clothing import Clothing
from .models.bin import Bin
from .models.user import User
from .models.order import Order
from .models.favorite import Favorite
from .models.order_content import OrderContent
import app.models
from .schemas import ClothingSimpleSchema, ClothingAdditionalSchema, ClothingColoredSchema, OrderCreateSchema,OrderCreateInfoSchema, FavoriteSchema, ClothingDetailSchema, OrderDetailSchema, OrderCatalogSchema,UserPasswordUpdate

from .models.user import User
from .schemas import ClothingSimpleSchema, UserCreate, UserLogin, UserUpdate

from .schemas import (
    ClothingSimpleSchema,
    ClothingDetailSchema,
    ClothingAdditionalSchema,
    ClothingColoredSchema,
    OrderCreateInfoSchema,
    OrderCatalogSchema,
    OrderDetailSchema,
    OrderCreateSchema,
    UserCreate,
    UserLogin,
    UserUpdate,
    FavoriteCreate,
    FavoriteSchema,
    CartItemCreate
)

router = APIRouter()
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

@router.get("/simple-list", response_model=list[ClothingSimpleSchema])
async def get_clothes_list(db: AsyncSession = Depends(get_db)):
    query = (
        select(Clothing)
        .where(
            Clothing.quantity >= 1,
        )
        .order_by(Clothing.id)
    )

    result = await db.execute(query)
    clothes = result.scalars().all()

    return clothes


@router.get("/search", response_model=list[ClothingSimpleSchema])
async def search_clothing(
        title: str,
        db: AsyncSession = Depends(get_db)
):
    search_term = title.strip()
    query = (
        select(Clothing)
        .where(
            or_(
                Clothing.name.ilike(f"%{search_term}%"),
                Clothing.type.ilike(f"%{search_term}%")
            )
        )
    )
    result = await db.execute(query)
    items = result.scalars().unique().all()
    return items


@router.get("/filter", response_model=list[ClothingSimpleSchema])
async def filter_clothing(
        clothing_type: str = None,
        color: str = None,
        min_price: float = None,
        max_price: float = None,
        db: AsyncSession = Depends(get_db)
):
    query = select(Clothing)
    if clothing_type:
        query = query.where(Clothing.type.ilike(clothing_type))
    if color:
        query = query.where(Clothing.color.ilike(color))
    if min_price is not None:
        query = query.where(Clothing.price >= min_price)
    if max_price is not None:
        query = query.where(Clothing.price <= max_price)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/favorites/add")
async def add_to_favorites(
        data: FavoriteCreate,
        user_id: int,  # Поки що беремо ID з параметрів
        db: AsyncSession = Depends(get_db)
):
    existing_favorite = await db.execute(
        select(Favorite).where(
            Favorite.id_user == user_id,
            Favorite.id_clothing == data.id_clothing
        )
    )
    if existing_favorite.scalars().first():
        return {"message": "Товар вже в обраному"}

    new_favorite = Favorite(
        id_user=user_id,
        id_clothing=data.id_clothing
    )

    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return {"status": "success", "favorite_id": new_favorite.id}


@router.post("/cart/add")
async def add_to_cart(
        data: CartItemCreate,
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(Cart).where(
        Cart.id_user == user_id,
        Cart.id_clothing == data.id_clothing
    )
    result = await db.execute(query)
    existing_item = result.scalar_one_or_none()

    if existing_item:
        existing_item.quantity += data.quantity
        await db.commit()
        return {"status": "updated", "new_quantity": existing_item.quantity}

    new_cart_item = Cart(
        id_user=user_id,
        id_clothing=data.id_clothing,
        quantity=data.quantity
    )

    db.add(new_cart_item)
    await db.commit()
    await db.refresh(new_cart_item)

    return {"status": "success", "cart_item_id": new_cart_item.id}


@router.get("/clothing/{clothing_id}", response_model=ClothingDetailSchema)
async def get_clothing_detail(
        clothing_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(Clothing).where(Clothing.id == clothing_id)

    result = await db.execute(query)
    clothing = result.scalar_one_or_none()

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing not found")

    return clothing


@router.get("/additional", response_model=list[ClothingAdditionalSchema])
async def get_other_colors_sizes(clname: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(Clothing)
        .where(
            Clothing.name == clname,
        )
    )

    result = await db.execute(query)
    clothes = result.scalars().all()

    return clothes


@router.get("/colored", response_model=list[ClothingColoredSchema])
async def get_other_sizes_for_colored(clname: str, clcolor: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(Clothing)
        .where(
            Clothing.name == clname,
            Clothing.color == clcolor,
        )
    )

    result = await db.execute(query)
    clothes = result.scalars().all()

    return clothes


@router.post("/register")
async def register_user(userData: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = hash_password(userData.password)
    newUser = User(
        first_name=userData.first_name,
        last_name=userData.last_name,
        phone_number=userData.phone_number,
        email=userData.email,
        password = hashed_password

    )
    db.add(newUser)
    await db.commit()
    await db.refresh(newUser)
    return {"message": "User created successfully", "user": newUser}


# routers.py
@router.post("/login")
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")

    matched_password = verify_password(payload.password, user.password)
    if not matched_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неправильний email або пароль")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Записуємо обидва токени в кукі
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite="lax",
        secure=False,  # Зміни на True для HTTPS в продакшені
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )
    return {"message": "Успішний вхід"}

@router.patch("/users/me/password")
async def change_password(payload:UserPasswordUpdate, current_user:AsyncSession=Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    print(payload)
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поточний пароль невірний"
        )

    current_user.password = hash_password(payload.new_password)

    try:
        db.add(current_user)
        await db.commit()
        return {"message": "Пароль успішно змінено"}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Помилка сервера")
@router.post("/refresh")
async def refresh_access_token(
        response: Response,
        refresh_token: str | None = Cookie(default=None),
        db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(data={"sub": str(user_id)})

    # Оновлюємо куку з новим access токеном
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite="lax",
        secure=False,
    )
    return {"message": "Token refreshed"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Успішний вихід"}


@router.get("/users/me")
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


@router.patch("/users/me")
async def update_user(payload: UserUpdate, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data to update is not provided")
    for key, value in update_data.items():
        setattr(current_user, key, value)
    try:
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return {"message": "User updated successfully", "user": current_user}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating user")


@router.get("/favorites", response_model=List[FavoriteSchema])
async def get_favorites(
        current_user: User = Depends(get_current_user), # Від petro (безпечно)
        db: AsyncSession = Depends(get_db)
):
    query = (
        select(Favorite)
        .options(selectinload(Favorite.clothing))
        .where(Favorite.id_user == current_user.id)
    )

    result = await db.execute(query)
    favorites = result.scalars().all()

    return list(favorites)

# ДОДАНО ВІД MISHA
@router.get("/cart")
async def get_user_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = (
        select(Bin, Clothing).
        join(Clothing, Bin.id_clothing == Clothing.id).
        where(Bin.id_user == current_user.id))
    result = await db.execute(query)
    cart_items = result.all()
    print(cart_items)
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

# ВІД PETRO (з перевіркою безпеки на current_user)
@router.get("/orders/{order_id}", response_model=OrderDetailSchema)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Order)
        .options(
            selectinload(Order.order_content)
            .selectinload(OrderContent.clothing)
        )
        .where(Order.id == order_id, Order.id_user == current_user.id)
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ВІД PETRO (отримуємо замовлення тільки поточного юзера)
@router.get("/orders", response_model=List[OrderCatalogSchema])
async def get_orders_catalog(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(
            Order.id,
            Order.cost,
            Order.delivery_company,
            Order.date,
            func.count(OrderContent.id).label("items_count")
        )
        .outerjoin(OrderContent, Order.id == OrderContent.id_order)
        .group_by(Order.id)
        .where(Order.id_user == current_user.id)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": row.id,
            "cost": row.cost,
            "delivery_company": row.delivery_company,
            "date": row.date,
            "items_count": row.items_count
        }
        for row in rows
    ]

# ДОДАНО ВІД MISHA
@router.get("/new-order-info", response_model=OrderCreateInfoSchema)
async def get_info_for_new_order(user_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    query = (
        select(User)
        .where(
            User.id == user_id,
        )
    )

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user



@router.post("/create-order", status_code=status.HTTP_201_CREATED)
async def create_order(
        payload: OrderCreateSchema,
        db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, payload.id_user)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.city = payload.city
    user.street = payload.street
    user.house_number = payload.house_number

    new_order = Order(
        cost=payload.cost,
        delivery_company=payload.delivery_company,
        delivery_type=payload.delivery_type,
        postal_number=payload.postal_number,
        id_user=payload.id_user,
        date=datetime.now()
    )

    db.add(new_order)
    await db.flush()

    for item_id in payload.id_clothing:
        new_order_content = OrderContent(
            id_clothing=item_id,
            id_order=new_order.id
        )
        db.add(new_order_content)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка при збереженні: {str(e)}")

    return {
        "status": "success",
        "message": f"Замовлення створено"
    }

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request,response: Response, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка авторизації Google: {str(e)}"
        )

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Не вдалося отримати дані користувача від Google")

    email = user_info.get('email')
    first_name = user_info.get('given_name')
    last_name = user_info.get('family_name')

    # 3. Шукаємо користувача в нашій базі даних за email
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 4. Якщо користувача немає в базі - створюємо його (Реєстрація)
    if not user:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=None
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response = RedirectResponse(url="http://localhost:3000/me")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite="lax",
        secure=False,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    return response
