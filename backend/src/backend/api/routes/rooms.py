import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.crud import message, room
from backend.events.chat_connections import disconnect_user_from_room
from backend.events.redis_events import publish_chat_event
from backend.models import Room
from backend.schemas.message import (
    MessageCreateUser,
    MessagePublic,
    RoomMessagePublic,
    RoomMessagesPublic,
)
from backend.schemas.redis import RedisEvent
from backend.schemas.room import RoomCreate, RoomPublic, RoomsPublic
from backend.schemas.room_user import RoomUserPublic

router = APIRouter(prefix="/rooms",tags=["Rooms"])

@router.get("/",response_model=RoomsPublic)
def read_rooms(
    session: SessionDep, 
    current_user: CurrentUser,
    limit: int = 10,
    offset: int = 0):
    rooms, count = room.get_rooms(session,limit,offset)
    rooms_public = [RoomPublic.model_validate(db_room) for db_room in rooms]
    return RoomsPublic(data=rooms_public,count=count)

@router.get("/id/{room_id}",response_model=RoomPublic)
def read_room_by_id(
    session: SessionDep, 
    current_user: CurrentUser,
    room_id: uuid.UUID
):
    existing_room = session.get(Room,room_id)
    if not existing_room:
          raise HTTPException(status_code=404,detail="Room not found")
    return existing_room

@router.get("/messages/id/{room_id}",response_model=RoomMessagesPublic)
def get_room_messages(
    session: SessionDep,
    current_user: CurrentUser,
    room_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0) -> RoomMessagesPublic:
    existing_room = session.get(Room,room_id)
    if not existing_room:
          raise HTTPException(status_code=404,detail="Room not found")
    messages, count = message.read_messages_in_room(session,room_id,limit,offset)
    messages_public = [RoomMessagePublic.model_validate(db_message) for db_message in messages]
    return RoomMessagesPublic(data=messages_public,count=count)

@router.post("/",response_model=RoomPublic)
def create_room(
    session: SessionDep,
    current_user: CurrentUser,
    room_in: RoomCreate
):
    return room.create_room(session,room_in,current_user.id)

@router.delete("/id/{room_id}",dependencies=[Depends(get_active_superuser)])
def delete_room(
    session: SessionDep,
    room_id: uuid.UUID):
    existing_room = session.get(Room,room_id)
    if not existing_room:
          raise HTTPException(status_code=404,detail="Room not found")
    room.delete_room(session,existing_room)
    return "Room was successfully deleted"

@router.post("/message/id/{room_id}",response_model=MessagePublic)
async def send_message(
    session: SessionDep, 
    request: Request,
    current_user: CurrentUser,
    room_id: uuid.UUID,
    message_user_in: MessageCreateUser):
    existing_room = session.get(Room,room_id)
    if not existing_room:
        raise HTTPException(status_code=404,detail="Room not found")
    user_in_room = room.get_user_in_room(session,room_id, current_user.id)
    if not user_in_room:
        raise HTTPException(status_code=403,detail="You have to join room first before sending any message there")
    created_message = room.send_message(session,message_user_in,room_id,current_user.id)
    await publish_chat_event(
        request.app.state.redis,
        RedisEvent(
            event="message_created",
            room_id=room_id,
            message=MessagePublic.model_validate(created_message),
        ),
    )
    return created_message


@router.delete(
    "/id/{room_id}/users/id/{user_id}",
    dependencies=[Depends(get_active_superuser)])
async def kick_user(session: SessionDep, room_id: uuid.UUID, user_id:uuid.UUID):
    existing_room = session.get(Room,room_id)
    if not existing_room:
        raise HTTPException(status_code=404,detail="Room not found")
    user_in_room = room.get_user_in_room(session,room_id, user_id)
    if not user_in_room:
        raise HTTPException(status_code=404,detail="The room and user are not related")
    room.leave_room(session,user_in_room)
    await disconnect_user_from_room(user_id, room_id)
    return "User was successfully disconnected from the room"

@router.post("/join/id/{room_id}",response_model=RoomUserPublic)
def join_room(
    session: SessionDep, 
    current_user: CurrentUser,
    room_id: uuid.UUID):
    existing_room = session.get(Room,room_id)
    if not existing_room:
        raise HTTPException(status_code=404,detail="Room not found")
    user_in_room = room.get_user_in_room(session,room_id, current_user.id)
    if user_in_room:
        raise HTTPException(status_code=403,detail="You already in the room")
    room_user = room.join_room(session,room_id,current_user.id)
    return room_user

@router.delete("/leave/id/{room_id}")
async def leave_room(
    session: SessionDep, 
    current_user: CurrentUser,
    room_id: uuid.UUID):
    existing_room = session.get(Room,room_id)
    if not existing_room:
        raise HTTPException(status_code=404,detail="Room not found")
    user_in_room = room.get_user_in_room(session,room_id, current_user.id)
    if not user_in_room:
        raise HTTPException(status_code=404,detail="The room and user are not related")
    room.leave_room(session,user_in_room)
    await disconnect_user_from_room(current_user.id, room_id)
    return "You successfully left the room"