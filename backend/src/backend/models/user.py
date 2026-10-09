
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC

if TYPE_CHECKING:
    from backend.models import Comment, Friendship, Message, Post

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    username: str = Field(nullable=False,index=True,max_length=127)
    created_at: datetime = Field(
        default_factory=get_datetime_UTC,
        sa_type=DateTime(timezone=True)
    )
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

    posts: list["Post"] = Relationship(back_populates="owner",cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="owner",cascade_delete=True)

    friendships_requestor: list["Friendship"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Friendship.requestor_id"},
        back_populates="requestor", cascade_delete=True)
    friendships_receiver: list["Friendship"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Friendship.receiver_id"}
        ,back_populates="receiver", cascade_delete=True)

    messages: list["Message"] = Relationship(back_populates="sender")