import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_user_token
from app.core.config import JWT_SECRET_KEY
from app.db.database import AsyncSessionLocal
from app.features.user.crud import get_user


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Залежність для отримання поточного користувача
@cache_user_token(ttl=900)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    # Читаємо токен виключно з кукі
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id_int = int(user_id)
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    user = await get_user(db, user_id_int)

    if user is None:
        raise credentials_exception

    return user
