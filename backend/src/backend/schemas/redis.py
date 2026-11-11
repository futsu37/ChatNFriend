import uuid

from sqlmodel import SQLModel

from backend.schemas.message import MessagePublic


class RedisEvent(SQLModel):
    event: str
    room_id: uuid.UUID
    message: MessagePublic