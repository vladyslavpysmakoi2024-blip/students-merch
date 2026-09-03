from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_IN_MINUTES,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_IN_DAYS,
)

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (), {"__version__": bcrypt.__version__})


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return token


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_IN_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
