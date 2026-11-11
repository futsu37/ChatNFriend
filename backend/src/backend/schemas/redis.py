import uuid
from typing import Literal

from sqlmodel import SQLModel

from backend.schemas.message import MessagePublic


class RedisEvent(SQLModel):
    event: Literal["message_created", "message_updated", "message_deleted"]
    room_id: uuid.UUID
    message: MessagePublic | None = None
    message_id: uuid.UUID | None = None