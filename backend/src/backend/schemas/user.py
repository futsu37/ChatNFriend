from backend.models import Post
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str = Field(min_length=1, max_length=127)
    password: str = Field(min_length=1, max_length=127)
    is_active: bool = True
    is_superuser: bool = False

class UserRegister(SQLModel):
    username: str = Field(min_length=1, max_length=127)
    password: str = Field(min_length=1, max_length=127)

class UserUpdateMe(SQLModel):
    username: str | None = Field(default=None,min_length=1, max_length=127)

class UserUpdate(UserUpdateMe):
    is_active: bool | None = True
    is_superuser: bool | None = False
    password: str | None = Field(default=None,min_length=1, max_length=127)
    
class UserPublic(SQLModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    is_active: bool
    is_superuser: bool
    posts: list[Post]

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


