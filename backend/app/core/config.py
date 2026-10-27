import os
from pathlib import Path

from dotenv import load_dotenv


def _env_flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() not in ("false", "0", "no", "")


BASE_DIR = Path(__file__).resolve().parent.parent.parent

if (BASE_DIR / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env")
elif (BASE_DIR.parent / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR.parent / ".env")
else:
    load_dotenv()

DEBUG = _env_flag("DEBUG", "false")
DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_SSL = os.getenv("DATABASE_SSL", "disable" if DB_HOST in ("localhost", "127.0.0.1") else "require")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey12345_students_merch_shop")
ACCESS_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_IN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_IN_DAYS", "7"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

MONOBANK_TOKEN = os.getenv("MONOBANK_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")

is_production = (
    not DEBUG
    or (FRONTEND_URL and "https://" in FRONTEND_URL and "localhost" not in FRONTEND_URL)
    or os.getenv("RENDER") is not None
    or os.getenv("VERCEL") is not None
)

DEFAULT_COOKIE_SECURE = "true" if is_production else "false"
COOKIE_SECURE = _env_flag("COOKIE_SECURE", DEFAULT_COOKIE_SECURE)

DEFAULT_COOKIE_SAMESITE = "none" if (COOKIE_SECURE or is_production) else "lax"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", DEFAULT_COOKIE_SAMESITE).strip().lower()

REDIS_TIMEOUT = float(os.getenv("REDIS_TIMEOUT", "1"))
CACHE_ENABLED = _env_flag("CACHE_ENABLED", "true")
USE_VERCEL_KV = bool(os.getenv("KV_REST_API_URL"))

RATE_LIMIT_ENABLED = _env_flag("RATE_LIMIT_ENABLED", "true")
GLOBAL_RATE_LIMIT = int(os.getenv("GLOBAL_RATE_LIMIT", "300"))  # запитів за хвилину з одного IP
IP_BAN_STRIKES = int(os.getenv("IP_BAN_STRIKES", "5"))  # стільки вікон з перевищенням ліміту за годину -> бан IP
IP_BAN_SECONDS = int(os.getenv("IP_BAN_SECONDS", "900"))
BOT_BLOCK_ENABLED = _env_flag("BOT_BLOCK_ENABLED", "false" if DEBUG else "true")  # локально curl працює
ON_VERCEL = os.getenv("VERCEL") is not None
# Довіряємо X-Forwarded-For лише за проксі платформи, інакше клієнт підставить будь-який IP
TRUST_PROXY_HEADERS = _env_flag("TRUST_PROXY_HEADERS", "true" if ON_VERCEL or os.getenv("RENDER") else "false")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    if not all([DB_USER, DB_PASSWORD, DB_NAME, DB_HOST]):
        raise ValueError("Не знайдено всі необхідні змінні середовища для бази даних!")
    SSL_PARAM = f"?ssl={DB_SSL}" if DB_SSL and DB_SSL != "disable" else ""
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}{SSL_PARAM}"
