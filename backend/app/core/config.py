import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if (BASE_DIR / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env")
elif (BASE_DIR.parent / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR.parent / ".env")
else:
    load_dotenv()

DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_SSL = os.getenv(
    "DATABASE_SSL", "disable" if DB_HOST in ("localhost", "127.0.0.1") else "require"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "supersecretjwtkey12345_students_merch_shop"
)
ACCESS_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_IN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_IN_DAYS", "7"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    if not all([DB_USER, DB_PASSWORD, DB_NAME, DB_HOST]):
        raise ValueError("Не знайдено всі необхідні змінні середовища для бази даних!")
    SSL_PARAM = f"?ssl={DB_SSL}" if DB_SSL and DB_SSL != "disable" else ""
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}{SSL_PARAM}"
