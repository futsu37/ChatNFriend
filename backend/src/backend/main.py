from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.main import api_router
from backend.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"

app = FastAPI()

app.include_router(api_router,prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:8000","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.frontend("/",directory=FRONTEND_DIR)