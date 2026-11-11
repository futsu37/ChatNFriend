import asyncio
import logging

from backend.events.chat_connections import broadcast_room_event
from backend.events.redis_events import CHAT_EVENTS_CHANNEL
from backend.schemas.redis import RedisEvent
from pydantic import ValidationError
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def listen_for_chat_events(
    redis: Redis,
    ready: asyncio.Event | None = None,
) -> None:
    pubsub = redis.pubsub()

    try:
        await pubsub.subscribe(CHAT_EVENTS_CHANNEL)
        logger.info("Subscribed to %s", CHAT_EVENTS_CHANNEL)
        if ready is not None:
            ready.set()

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                event = RedisEvent.model_validate_json(message["data"])
                if event.event in {"message_created", "message_updated"}:
                    if event.message is None:
                        logger.error("Chat event %s is missing its message", event.event)
                        continue
                    await broadcast_room_event(
                        event.room_id,
                        event.message.model_dump(mode="json")
                        if event.event == "message_created"
                        else {
                            "event": event.event,
                            "message": event.message.model_dump(mode="json"),
                        },
                    )
                elif event.message_id is not None:
                    await broadcast_room_event(
                        event.room_id,
                        {
                            "event": event.event,
                            "room_id": str(event.room_id),
                            "message_id": str(event.message_id),
                        },
                    )
                else:
                    logger.error("Chat event %s is missing its message ID", event.event)

            except (ValidationError, TypeError, ValueError):
                logger.exception("Failed to decode chat event")

    except asyncio.CancelledError:
        logger.info("Chat event listener cancelled")
        raise

    finally:
        await pubsub.unsubscribe(CHAT_EVENTS_CHANNEL)
        await pubsub.aclose()
        logger.info("Unsubscribed from %s", CHAT_EVENTS_CHANNEL)
