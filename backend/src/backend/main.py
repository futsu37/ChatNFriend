from pathlib import Path

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.main import api_router
from backend.core.app import app
from backend.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"

app.include_router(api_router,prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:8000","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.frontend("/",directory=FRONTEND_DIR)

@app.get("/test-redis")
async def test_redis(request: Request):
    redis = request.app.state.redis

    await redis.set("hello", "world")
    value = await redis.get("hello")

    return {"redis": value}