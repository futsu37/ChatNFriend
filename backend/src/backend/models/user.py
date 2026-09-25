import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from backend.utils.time import get_datetime_UTC


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