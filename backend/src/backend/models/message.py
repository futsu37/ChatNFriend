import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC

if TYPE_CHECKING:
    from backend.models import Room, User

class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    content: str = Field(max_length=1027,nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=get_datetime_UTC
    )
    room_id: uuid.UUID = Field(foreign_key="room.id",ondelete="CASCADE")
    sender_id: uuid.UUID = Field(nullable=True,foreign_key="user.id",ondelete="SET NULL")
    
    sender: "User" = Relationship(back_populates="messages")
    room: "Room" = Relationship(back_populates="messages")