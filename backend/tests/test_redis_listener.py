import asyncio
import uuid

from backend.events import redis_listener
from backend.schemas.message import MessagePublic
from backend.schemas.redis import RedisEvent


class FakePubSub:
    def __init__(self, messages: list[dict[str, object]]):
        self.messages = messages
        self.unsubscribed = False
        self.closed = False

    async def subscribe(self, channel: str) -> None:
        assert channel == "chat:events"

    async def listen(self):
        for message in self.messages:
            yield message

    async def unsubscribe(self, channel: str) -> None:
        assert channel == "chat:events"
        self.unsubscribed = True

    async def aclose(self) -> None:
        self.closed = True


class FakeRedis:
    def __init__(self, pubsub: FakePubSub):
        self.pubsub_connection = pubsub

    def pubsub(self) -> FakePubSub:
        return self.pubsub_connection


def test_listener_forwards_create_update_and_delete_events(monkeypatch) -> None:
    room_id = uuid.uuid4()
    message = MessagePublic(
        id=uuid.uuid4(),
        content="hello",
        room_id=room_id,
        sender_id=uuid.uuid4(),
        created_at="2026-11-11T00:00:00Z",
    )
    events = [
        RedisEvent(event="message_created", room_id=room_id, message=message),
        RedisEvent(event="message_updated", room_id=room_id, message=message),
        RedisEvent(
            event="message_deleted",
            room_id=room_id,
            message_id=message.id,
        ),
    ]
    pubsub = FakePubSub([
        {
            "type": "message",
            "data": event.model_dump_json(),
        }
        for event in events
    ])
    redis = FakeRedis(pubsub)
    received: list[tuple[uuid.UUID, dict[str, object]]] = []

    async def record_broadcast(
        target_room_id: uuid.UUID,
        payload: dict[str, object],
    ) -> None:
        received.append((target_room_id, payload))

    monkeypatch.setattr(redis_listener, "broadcast_room_event", record_broadcast)

    asyncio.run(redis_listener.listen_for_chat_events(redis))

    assert received == [
        (room_id, message.model_dump(mode="json")),
        (
            room_id,
            {
                "event": "message_updated",
                "message": message.model_dump(mode="json"),
            },
        ),
        (
            room_id,
            {
                "event": "message_deleted",
                "room_id": str(room_id),
                "message_id": str(message.id),
            },
        ),
    ]
    assert pubsub.unsubscribed
    assert pubsub.closed
