import uuid

from sqlmodel import Session, col, select

from backend.models import Message


def read_messages_in_room(
    session: Session,
    room_id: uuid.UUID,
    limit: int,
    offset: int):
    statement = select(Message).where(Message.room_id == room_id).order_by(col(Message.created_at).desc()).offset(offset).limit(limit)
    messages = session.exec(statement).all()
    count = messages.__len__()
    return messages, count