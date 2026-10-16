import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from backend.schemas.room_user import RoomUserPublicUser


class RoomPublic(SQLModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    users_in: list[RoomUserPublicUser]

class RoomsPublic(SQLModel):
    data: list[RoomPublic]
    count: int

class RoomCreate(SQLModel):
    name: str = Field(max_length=127,nullable=False)

class RoomUpdate(SQLModel):
    name: str | None = Field(default=None,max_length=127,nullable=False)