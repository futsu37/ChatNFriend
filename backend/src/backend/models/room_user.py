import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models import Room, User

class RoomUser(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "user_id",
            name="uq_room_user"
        ),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    
    room_id: uuid.UUID = Field(foreign_key="room.id",ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user.id",ondelete="CASCADE")

    user: "User" = Relationship(back_populates="rooms_in")
    room: "Room" = Relationship(back_populates="users_in")

    
