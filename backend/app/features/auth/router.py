import jwt
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.auth.crud as crud_auth
import app.features.user.crud as crud_user
from app.api.dependencies import get_db
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_IN_MINUTES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    JWT_SECRET_KEY,
    FRONTEND_URL
)
from app.core.schemas import MessageResponse
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.features.auth.schemas import UserGoogleCreate
from app.features.user.schemas import UserAndMessageResponse, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserAndMessageResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud_user.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exist")

    new_user = await crud_user.create_user(db, user_data)
    return {"message": "User created successfully", "user": new_user}


@router.post("/login", response_model=MessageResponse)
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_email(db, email=payload.email)
    if not user or not user.password or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite="none",  # 👈 Дозволяє передачу куків між різними доменами
        secure=True
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="none",  # 👈 Дозволяє передачу куків між різними доменами
        secure=True
    )

    return {"message": "Successful login"}


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successful logout"}


@router.post("/refresh", response_model=MessageResponse)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    # 1. Декодуємо токен
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY,
                             algorithms=["HS256"])
        user_id_str: str = payload.get("sub")

        if user_id_str is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = int(user_id_str)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    # 2. Перевіряємо, чи користувач досі існує в базі даних (використовуємо CRUD)
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    # 3. Генеруємо новий access токен
    new_access_token = create_access_token(data={"sub": str(user.id)})

    # 4. Оновлюємо куку
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite="lax",
        secure=False,  # Змініть на True у продакшені (HTTPS)
    )

    return {"message": "Token refreshed"}


# Налаштування OAuth
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login/google")
async def login_google(request: Request):
    # 'auth_callback' — це ім'я функції нижче
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authorization error: {exc!s}",
        ) from exc

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve user data from Google",
        )

    email = user_info.get("email")
    first_name = user_info.get("given_name")
    last_name = user_info.get("family_name")

    # 1. Перевіряємо, чи є користувач через CRUD
    user = await crud_user.get_user_by_email(db, email=email)

    # 2. Якщо немає - реєструємо через CRUD
    if not user:
        user_data = UserGoogleCreate(
            email=email, first_name=first_name, last_name=last_name)
        user = await crud_auth.create_user_google(db=db, user_in=user_data)

    # 3. Генеруємо токени
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 4. Створюємо відповідь-редірект на фронтенд
    response = RedirectResponse(url=f"{FRONTEND_URL}/me")

    # 5. Встановлюємо кукі
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
