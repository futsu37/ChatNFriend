import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import Engine
from sqlmodel import Session

from backend.api.deps import EngineDep, get_current_user
from backend.crud import room
from backend.models import Room
from backend.schemas.message import MessageCreateUser

router = APIRouter()
class UserWebSocket:
    user_id: uuid.UUID
    websocket: WebSocket
    def __init__(self, user_id: uuid.UUID, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket

user_room_connections: dict[uuid.UUID,list[UserWebSocket]] = {}


async def disconnect_user_from_room(user_id: uuid.UUID, room_id: uuid.UUID) -> None:
    room_connections = user_room_connections.get(room_id, [])
    for connection in room_connections.copy():
        if connection.user_id == user_id:
            room_connections.remove(connection)
            await connection.websocket.close(code=1008, reason="Room membership revoked")
    if not room_connections:
        user_room_connections.pop(room_id, None)


@router.websocket("/ws/room/id/{room_id}/")
async def room_user_connection(
    websocket: WebSocket,
    engine: EngineDep,
    room_id: uuid.UUID) -> None:
    
    user_id = ws_room_check(engine,websocket,room_id)
    user_websocket = UserWebSocket(user_id,websocket)
    offered_protocols = {
        protocol.strip()
        for protocol in websocket.headers.get("sec-websocket-protocol", "").split(",")
    }
    await websocket.accept(
        subprotocol="chat" if "chat" in offered_protocols else None,
    )
    try:
        
        if user_room_connections.get(room_id) == None:
            user_room_connections[room_id] = []
        user_room_connections[room_id].append(user_websocket)

        while True:
            ws_room_check(engine,websocket,room_id)
            message = await websocket.receive_text()

            await send_message_in_room(engine, websocket,message,room_id,user_id)

    except WebSocketDisconnect:
        room_connections = user_room_connections.get(room_id, [])
        if user_websocket in room_connections:
            room_connections.remove(user_websocket)

    finally:
        room_connections = user_room_connections.get(room_id, [])
        if user_websocket in room_connections:
            room_connections.remove(user_websocket)
        if not room_connections:
            user_room_connections.pop(room_id, None)

def ws_room_check(engine: Engine, websocket: WebSocket, room_id: uuid.UUID) -> uuid.UUID:
    with Session(engine) as session:
        data: str | None = websocket.headers.get("authorization")
        if data and data.lower().startswith("bearer "):
            data = data[7:]
        else:
            protocols = websocket.headers.get("sec-websocket-protocol", "").split(",")
            token_protocol = next(
                (
                    protocol.strip()
                    for protocol in protocols
                    if protocol.strip().startswith("access_token.")
                ),
                None,
            )
            data = token_protocol.removeprefix("access_token.") if token_protocol else None
        if not data:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        current_user = get_current_user(session,data)
        existing_room = session.get(Room, room_id)
        if not existing_room:
            raise HTTPException(status_code=404,detail="Room not found")

        user_in_room = room.get_user_in_room(session,room_id, current_user.id)
        if not user_in_room:
            raise HTTPException(status_code=404,detail="The room and user are not related")
        return current_user.id

async def send_message_in_room( 
    engine: Engine, 
    websocket: WebSocket, 
    message: str, 
    room_id: uuid.UUID,
    sender_id: uuid.UUID):
    ws_room_check(engine,websocket,room_id)
    message_schema = MessageCreateUser(content=message)
    with Session(engine) as session:
        full_message = room.send_message(session=session,user_message_in=message_schema,room_id=room_id,user_id=sender_id)
    await broadcast_room_message(room_id, full_message.model_dump(mode="json"))


async def broadcast_room_message(room_id: uuid.UUID, message: dict[str, object]) -> None:
    connections = user_room_connections.get(room_id, [])
    for connection in connections:
        await connection.websocket.send_json(message)


async def broadcast_message_updated(
    room_id: uuid.UUID,
    message: dict[str, object],
) -> None:
    await broadcast_room_message(
        room_id,
        {"event": "message_updated", "message": message},
    )


async def broadcast_message_deleted(
    room_id: uuid.UUID,
    message_id: uuid.UUID,
) -> None:
    await broadcast_room_message(
        room_id,
        {
            "event": "message_deleted",
            "room_id": str(room_id),
            "message_id": str(message_id),
        },
    )
    
