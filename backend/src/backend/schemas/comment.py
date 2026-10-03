import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class CommentPublic(SQLModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    owner_id: uuid.UUID
    post_id: uuid.UUID

class CommentsPublic(SQLModel):
    data: list[CommentPublic]
    count: int

class CommentCreate(SQLModel):
    content: str = Field(min_length=1, max_length=511, nullable=False)

class CommentUpdate(SQLModel):
    content: str | None = Field(default=None, min_length=1, max_length=511)
