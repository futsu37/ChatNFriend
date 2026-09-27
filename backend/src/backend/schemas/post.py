import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PostPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: str
    owner_id: uuid.UUID
    created_at: datetime

class PostsPublic(SQLModel):
    data: list[PostPublic]
    count: int

class PostCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=511)

class PostUpdateMe(SQLModel):
    title: str | None = Field(default=None,min_length=1, max_length=255)
    description: str | None = Field(default=None,min_length=1, max_length=511)

class PostUpdate(SQLModel):
    title: str | None = Field(default=None,min_length=1, max_length=255)
    description: str | None = Field(default=None,min_length=1, max_length=511)
    owner_id: uuid.UUID | None = None