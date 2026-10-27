import jwt
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.auth.crud as crud_auth
import app.features.user.crud as crud_user
from app.api.dependencies import get_db
from app.core.cache import invalidate_user_cache
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_IN_MINUTES,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    JWT_SECRET_KEY,
)
from app.core.schemas import MessageResponse
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.features.auth.schemas import UserGoogleCreate
from app.features.user.schemas import UserAndMessageResponse, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _cookie_params(request: Request) -> tuple[str, bool]:
    is_https = COOKIE_SECURE or request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    samesite_policy = "none" if is_https else (COOKIE_SAMESITE or "lax")
    return samesite_policy, is_https


@router.post("/register", response_model=UserAndMessageResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud_user.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exist")

    new_user = await crud_user.create_user(db, user_data)
    return {"message": "User created successfully", "user": new_user}


@router.post("/login", response_model=MessageResponse)
async def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get_user_by_email(db, email=payload.email)
    if not user or not user.password or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    samesite_policy, is_https = _cookie_params(request)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite=samesite_policy,
        secure=is_https,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite=samesite_policy,
        secure=is_https,
    )

    return {"message": "Successful login"}


@router.post("/logout")
@router.post("/auth/logout")
async def logout(
    request: Request,
    response: Response,
    access_token: str | None = Cookie(default=None),
):
    if access_token:
        try:
            payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            payload = {}
        if payload.get("sub"):
            await invalidate_user_cache(payload["sub"])

    samesite_policy, is_https = _cookie_params(request)

    response.delete_cookie(
        key="access_token",
        samesite=samesite_policy,
        secure=is_https,
        httponly=True,
    )
    response.delete_cookie(
        key="refresh_token",
        samesite=samesite_policy,
        secure=is_https,
        httponly=True,
    )

    return {"message": "Успішний вихід"}


@router.post("/refresh", response_model=MessageResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")

        if user_id_str is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = int(user_id_str)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    new_access_token = create_access_token(data={"sub": str(user.id)})
    samesite_policy, is_https = _cookie_params(request)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite=samesite_policy,
        secure=is_https,
    )

    return {"message": "Token refreshed"}


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
    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        user_data = UserGoogleCreate(
            email=email,
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
        )
        user = await crud_auth.create_user_google(db=db, user_in=user_data)

    frontend_base = (FRONTEND_URL or "http://localhost:3000").rstrip("/")
    response = RedirectResponse(url=f"{frontend_base}/me")
    samesite_policy, is_https = _cookie_params(request)

    response.set_cookie(
        key="access_token",
        value=create_access_token(data={"sub": str(user.id)}),
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
        samesite=samesite_policy,
        secure=is_https,
    )
    response.set_cookie(
        key="refresh_token",
        value=create_refresh_token(data={"sub": str(user.id)}),
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite=samesite_policy,
        secure=is_https,
    )

    return response
