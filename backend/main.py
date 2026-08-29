import os, sys
import uvicorn

from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers import auth, clothing, cart, favorite, order, user

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

app = FastAPI()

# noinspection PyTypeChecker
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-fallback-secret-key-12345")
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clothing.router)
app.include_router(cart.router)
app.include_router(favorite.router)
app.include_router(order.router)
app.include_router(user.router)

if __name__ == "__main__":
    if "runserver" in sys.argv:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
