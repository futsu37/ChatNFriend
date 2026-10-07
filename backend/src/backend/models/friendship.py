import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from backend.utils.time import get_datetime_UTC


class Status(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

if TYPE_CHECKING:
    from backend.models import User

class Friendship(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    requestor_id: uuid.UUID = Field(foreign_key="user.id",ondelete="CASCADE",nullable=False)
    receiver_id: uuid.UUID = Field(foreign_key="user.id",ondelete="CASCADE",nullable=False)
    status: Status = Field(default=Status.PENDING)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=get_datetime_UTC
    )

    requestor: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys":"Friendship.requestor_id"},back_populates="friendships_requestor")
    receiver: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys":"Friendship.receiver_id"},
        back_populates="friendships_receiver")
