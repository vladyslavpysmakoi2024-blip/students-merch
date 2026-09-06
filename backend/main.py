import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import truststore
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import app as _models_registry  # noqa
from app.db.database import Base, engine
from app.features.auth.router import router as auth_router
from app.features.cart.router import router as cart_router
from app.features.clothing.router import router as clothing_router
from app.features.favorite.router import router as favorite_router
from app.features.order.router import router as order_router
from app.features.user.router import router as user_router
from app.features.promo.router import router as promo_router

truststore.inject_into_ssl()

env_file = Path(__file__).parent / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Students Merch Shop API", lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-fallback-secret-key-12345"),
)

cors_origins_env = os.getenv("CORS_ORIGINS")
origins = (
    [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]
    if cors_origins_env
    else [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(clothing_router)
app.include_router(cart_router)
app.include_router(favorite_router)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(promo_router)

if __name__ == "__main__":
    if "runserver" in sys.argv:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
