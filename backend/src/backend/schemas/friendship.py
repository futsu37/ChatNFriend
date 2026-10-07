import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from backend.models.friendship import Status


class FriendshipPublic(SQLModel):
    id: uuid.UUID
    created_at: datetime
    requestor_id: uuid.UUID
    receiver_id: uuid.UUID
    status: Status

class FriendshipCreate(SQLModel):
    receiver_id: uuid.UUID = Field(nullable=False)
    requestor_id: uuid.UUID = Field(nullable=False)

class FriendshipsPublic(SQLModel):
    data: list[FriendshipPublic]
    count: int

class FriendshipUpdate(SQLModel):
    status: Status
