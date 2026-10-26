import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from backend.api.deps import SessionDep
from backend.crud import room
from backend.models import Room, User

router = APIRouter()

history = []
connections: list[WebSocket] = []

user_room_connections: dict[uuid.UUID,list[WebSocket]] = {}
@router.websocket("/ws/echo")
async def echo(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        connections.append(websocket)
        while True:
            text = await websocket.receive_text()
            history.append(text)
            [await ws.send_text(text) for ws in connections]
    except WebSocketDisconnect:
            print("history: ")
            [print(message) for message in history]
            print("connections: ")
            [print(connection) for connection in connections]
            history.clear()
            connections.remove(websocket)
    finally:
        if websocket in connections:
            connections.remove(websocket)

@router.websocket("/ws/authorized/{user_id}")
async def authorized(
    session: SessionDep, 
    websocket: WebSocket, 
    user_id: uuid.UUID) -> None:
    existing_user = session.get(User,user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this id does not exist")
    await websocket.accept()
    try:
        connections.append(websocket)
        while True:
            await websocket.receive_text()
            text = "received by: " + existing_user.username
            await websocket.send_text(text)
    except WebSocketDisconnect:
            connections.remove(websocket)
    finally:
        if websocket in connections:
            connections.remove(websocket)

@router.websocket("/ws/user/id/{user_id}/room/id/{room_id}/")
async def room_user_connection(
    session: SessionDep,
    websocket: WebSocket,
    user_id: uuid.UUID,
    room_id: uuid.UUID) -> None:
    
    existing_user = session.get(User,user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this id does not exist")
    
    existing_room = session.get(Room, room_id)
    if not existing_room:
        raise HTTPException(status_code=404,detail="Room not found")
    
    user_in_room = room.get_user_in_room(session,room_id, user_id)
    if not user_in_room:
        raise HTTPException(status_code=404,detail="The room and user are not related")
    await websocket.accept()
    try:
        if user_room_connections.get(room_id) == None:
            user_room_connections[room_id] = []
        while True:
            user_room_connections[room_id].append(websocket)
            message = await websocket.receive_text()
            await send_message_in_room(message,room_id)
    except WebSocketDisconnect:
        user_room_connections[room_id].remove(websocket)
    finally:
        if websocket in user_room_connections[room_id]:
            user_room_connections[room_id].remove(websocket)


async def send_message_in_room(message: str, room_id: uuid.UUID):
    connections = user_room_connections[room_id]
    for connection in connections:
        await connection.send_text(message)
    
