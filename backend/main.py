import uvicorn
import sys
from pathlib import Path
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as specials_router
import app.models

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-fallback-secret-key-12345")
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(specials_router)

if __name__ == "__main__":
    if "runserver" in sys.argv:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
