import uuid
from operator import and_

from sqlmodel import Session, col, select

from backend.models import Message, Room, RoomUser
from backend.schemas.message import MessageCreate, MessageCreateUser
from backend.schemas.room import RoomCreate
from backend.schemas.room_user import RoomUserCreate


def get_rooms(session: Session, limit: int, offset: int):
    statement = select(Room).order_by(col(Room.created_at).desc()).offset(offset).limit(limit)
    rooms = session.exec(statement).all()
    count = rooms.__len__()
    return rooms, count

def leave_room(session: Session, user_in_room: RoomUser):
    session.delete(user_in_room)
    session.commit()

def get_user_in_room(session: Session, room_id: uuid.UUID, user_id: uuid.UUID) -> RoomUser | None:
    statement = select(RoomUser).where(
        and_(
            RoomUser.user_id == user_id,
            RoomUser.room_id == room_id
            ))
    user_in_room = session.exec(statement).first()
    return user_in_room

def join_room(session: Session, room_id: uuid.UUID, user_id: uuid.UUID) -> RoomUser:
    room_user_in = RoomUserCreate(room_id=room_id,user_id=user_id) 
    room_user = RoomUser.model_validate(room_user_in)
    session.add(room_user)
    session.commit()
    session.refresh(room_user)
    return room_user

def send_message(
    session: Session, 
    message_user_in: MessageCreateUser,
    room_id: uuid.UUID,
    user_id: uuid.UUID) -> Message:
    message_in = MessageCreate(
        content=message_user_in.content,
        room_id=room_id,
        sender_id=user_id)

    message = Message.model_validate(message_in)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def delete_room(session: Session, existing_room: Room):
    session.delete(existing_room)
    session.commit()

def create_room(session: Session, room_in: RoomCreate, user_id: uuid.UUID) -> Room:
    room = Room.model_validate(room_in)
    roomUserIn = RoomUserCreate(room_id=room.id,user_id=user_id)
    roomUser = RoomUser.model_validate(roomUserIn)
    session.add(room)
    session.add(roomUser)
    session.commit()
    session.refresh(room)
    session.refresh(roomUser)

    return room