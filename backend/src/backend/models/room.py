import uuid
from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel

from backend.utils.time import get_datetime_UTC

    
class Room(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    name: str = Field(max_length=127,nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=get_datetime_UTC
    )
