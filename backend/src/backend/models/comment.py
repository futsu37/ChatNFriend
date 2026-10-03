import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC

if TYPE_CHECKING:
    from backend.models import Post, User
    

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    content: str = Field(min_length=1, max_length=511,nullable=False)
    created_at: datetime = Field(
        default_factory=get_datetime_UTC,
        sa_type=DateTime(timezone=True)
    )
    owner_id: uuid.UUID = Field(foreign_key="user.id",nullable=False,ondelete="CASCADE")
    post_id: uuid.UUID = Field(foreign_key="post.id",nullable=False,ondelete="CASCADE")

    owner: "User" = Relationship(back_populates="comments")
    post: "Post" = Relationship(back_populates="comments")