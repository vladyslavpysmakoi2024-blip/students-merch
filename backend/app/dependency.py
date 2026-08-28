import os

from fastapi import Depends,Request, HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError

from app.models.user import User
from app.database import get_db,JWT_SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    # Читаємо токен з кукі замість заголовка
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
    except JWTError:
        raise credentials_exception

    query = select(User).where(User.id == user_id_int)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user