import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from backend.core.config import settings
from backend.events.redis_listener import listen_for_chat_events

logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    await redis.ping()
    app.state.redis = redis

    listener_ready = asyncio.Event()
    listener_task = asyncio.create_task(
        listen_for_chat_events(redis, listener_ready)
    )

    logger.info("Worker %s started", os.getpid())

    try:
        await asyncio.wait_for(listener_ready.wait(), timeout=10)
        yield

    finally:
        logger.info("Worker %s shutting down", os.getpid())

        listener_task.cancel()

        try:
            await listener_task
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Worker %s chat event listener failed", os.getpid())

        await redis.aclose()

        logger.info("Worker %s stopped", os.getpid())


app = FastAPI(lifespan=lifespan)