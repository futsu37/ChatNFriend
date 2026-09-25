import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str = Field(min_length=1, max_length=127)
    password: str = Field(min_length=1, max_length=127)
    is_active: bool = True
    is_superuser: bool = False

class UserPublic(SQLModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    is_active: bool
    is_superuser: bool

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


