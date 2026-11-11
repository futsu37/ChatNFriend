from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

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


app = FastAPI(lifespan=lifespan)