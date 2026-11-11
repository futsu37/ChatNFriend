import uuid

from fastapi import WebSocket, WebSocketDisconnect


class UserWebSocket:
    def __init__(self, user_id: uuid.UUID, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket


user_room_connections: dict[uuid.UUID, list[UserWebSocket]] = {}


async def disconnect_user_from_room(user_id: uuid.UUID, room_id: uuid.UUID) -> None:
    room_connections = user_room_connections.get(room_id, [])
    for connection in room_connections.copy():
        if connection.user_id == user_id:
            room_connections.remove(connection)
            await connection.websocket.close(code=1008, reason="Room membership revoked")
    if not room_connections:
        user_room_connections.pop(room_id, None)


async def broadcast_room_event(room_id: uuid.UUID, event: dict[str, object]) -> None:
    room_connections = user_room_connections.get(room_id, [])
    for connection in room_connections.copy():
        try:
            await connection.websocket.send_json(event)
        except (OSError, RuntimeError, WebSocketDisconnect):
            room_connections.remove(connection)

    if not room_connections:
        user_room_connections.pop(room_id, None)
