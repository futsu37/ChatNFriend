import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.user import User

class Post(SQLModel,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    title: str = Field(min_length=1, max_length=255,nullable=False)
    description: str = Field(min_length=1, max_length=511,nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="user.id",nullable=False,ondelete="CASCADE")
    
    owner: "User" = Relationship(back_populates="posts")