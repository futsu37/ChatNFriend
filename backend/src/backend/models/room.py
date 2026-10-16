import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import DateTime, Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC

if TYPE_CHECKING:
    from backend.models import Message, RoomUser
    
class Room(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    name: str = Field(max_length=127,nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=get_datetime_UTC
    )
    messages: list["Message"] = Relationship(back_populates="room",cascade_delete=True)
    users_in: list["RoomUser"] = Relationship(back_populates="room", cascade_delete=True)
