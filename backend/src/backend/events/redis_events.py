from backend.schemas.redis import RedisEvent
from redis.asyncio import Redis

CHAT_EVENTS_CHANNEL = "chat:events"


async def publish_chat_event(redis: Redis, event: RedisEvent) -> None:
    await redis.publish(CHAT_EVENTS_CHANNEL, event.model_dump_json())
