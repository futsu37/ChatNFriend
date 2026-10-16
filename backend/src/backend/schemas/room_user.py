import uuid

from sqlmodel import SQLModel


class RoomUserPublicUser(SQLModel):
    user_id: uuid.UUID

class RoomUserBase(SQLModel):
    room_id: uuid.UUID
    user_id: uuid.UUID

class RoomUserCreate(RoomUserBase):
    pass

class RoomUserPublic(RoomUserBase):
    pass