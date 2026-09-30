import os
import sys
from contextlib import asynccontextmanager

import truststore
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import CORS_ORIGINS, DEBUG, FRONTEND_URL
from app.db.database import Base, engine
from app.features.admin.router import router as admin_router
from app.features.auth.router import router as auth_router
from app.features.cart.router import router as cart_router
from app.features.clothing.router import router as clothing_router
from app.features.favorite.router import router as favorite_router
from app.features.order.router import router as order_router
from app.features.promo.router import router as promo_router
from app.features.survey.router import router as survey_router
from app.features.user.router import router as user_router

truststore.inject_into_ssl()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            from sqlalchemy import text
            from sqlalchemy.exc import SQLAlchemyError

            migrations = [
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS completed_survey BOOLEAN NOT NULL DEFAULT FALSE;',
                "ALTER TABLE survey_response ADD COLUMN IF NOT EXISTS assigned_package_id TEXT;",
                "ALTER TABLE survey_response ADD COLUMN IF NOT EXISTS is_package_confirmed BOOLEAN NOT NULL DEFAULT FALSE;",
                "INSERT INTO enum_status (data) SELECT v FROM (VALUES ('CREATED'), ('FAILED'), ('COMPLETED'), ('PROCESSING'), ('PAID')) AS t(v) WHERE NOT EXISTS (SELECT 1 FROM enum_status WHERE data = t.v);",
            ]
            for stmt in migrations:
                await conn.execute(text(stmt))
        except SQLAlchemyError as e:
            print(f"Startup migration notice: {e}", flush=True)
    yield


app = FastAPI(title="Students Merch Shop API", lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-fallback-secret-key-12345"),
)

origins = [orig.strip().rstrip("/") for orig in CORS_ORIGINS.split(",") if orig.strip()]
if FRONTEND_URL:
    clean_front = FRONTEND_URL.strip().rstrip("/")
    if clean_front and clean_front not in origins:
        origins.append(clean_front)

for default_origin in [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://students-merch-beta.vercel.app",
    "https://students-merch.vercel.app",
]:
    if default_origin not in origins:
        origins.append(default_origin)

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
app.include_router(survey_router)
app.include_router(admin_router)

if __name__ == "__main__":
    if "runserver" in sys.argv:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if DEBUG:
    import time

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
        print(f"⏱ Час виконання {request.method} {request.url.path}: {process_time:.4f} секунд")

        return response
