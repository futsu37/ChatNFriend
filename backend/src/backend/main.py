from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from backend.api.main import api_router
from backend.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )

    await redis.ping()
    app.state.redis = redis

    try:
        yield
    finally:
        await redis.aclose()

FRONTEND_DIR = Path(__file__).parent / "frontend"

app = FastAPI(lifespan=lifespan)

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