import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC

if TYPE_CHECKING:
    from backend.models.user import User

class Post(SQLModel,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    title: str = Field(min_length=1, max_length=255,nullable=False)
    description: str = Field(min_length=1, max_length=511,nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="user.id",nullable=False,ondelete="CASCADE")
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=get_datetime_UTC
    )
    
    owner: "User" = Relationship(back_populates="posts")