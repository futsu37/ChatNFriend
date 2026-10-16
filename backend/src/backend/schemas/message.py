import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class RoomMessagePublic(SQLModel):
    id: uuid.UUID
    content: str
    sender_id: uuid.UUID
    created_at: datetime

class RoomMessagesPublic(SQLModel):
    data: list[RoomMessagePublic]
    count: int

class MessagePublic(SQLModel):
    id: uuid.UUID
    content: str
    room_id: uuid.UUID
    sender_id: uuid.UUID
    created_at: datetime

class MessagesPublic(SQLModel):
    data: list[MessagePublic]
    count: int

class MessageCreateUser(SQLModel):
    content: str = Field(max_length=1027,nullable=False)

class MessageCreate(SQLModel):
    content: str = Field(max_length=1027,nullable=False)
    room_id: uuid.UUID
    sender_id: uuid.UUID

class MessageUpdate(SQLModel):
    content: str | None = Field(default=None,max_length=1027,nullable=False)