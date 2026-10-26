from fastapi.testclient import TestClient

from .utils.user import create_and_auth_user, get_user_me
from .utils.room import (
    create_room,
    delete_room,
    get_room,
    get_room_messages,
    join_room,
    kick_user,
    leave_room,
    send_message,
)

name = "test"
password = "testtest"

room_name = "Test Room"
message = "Test message"
def test_echo_websocket(client: TestClient):
    with client.websocket_connect("/api/v1/ws/echo") as websocket:
        websocket.send_text("test")
        assert websocket.receive_text() == "test"
        websocket.send_text("test2")
        assert websocket.receive_text() == "test2"

def test_two_connected_clients(client: TestClient):
    with client.websocket_connect("/api/v1/ws/echo") as websocket1:  # noqa: SIM117
        with client.websocket_connect("/api/v1/ws/echo") as websocket2:
            websocket1.send_text("send by websocket1")
            assert websocket2.receive_text() == "send by websocket1"
            assert websocket1.receive_text() == "send by websocket1"
            websocket2.send_text("send by websocket2")
            assert websocket2.receive_text() == "send by websocket2"
            assert websocket1.receive_text() == "send by websocket2"
            
def test_authorized_client(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    with client.websocket_connect(f"/api/v1/ws/authorized/{user_id}") as websocket:
        websocket.send_text("Authorized user")
        assert websocket.receive_text() == ("received by: " + name)

def test_room_message(client: TestClient):
    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    user1 = get_user_me(client=client,auth_headers=auth_headers1)
    user_id1 = user1["id"]
    user2 = get_user_me(client=client,auth_headers=auth_headers2)
    user_id2 = user2["id"]
    room1 = create_room(client=client,auth_headers=auth_headers1,name="room 1")
    room_id1 = room1["id"]
    room2 = create_room(client=client,auth_headers=auth_headers2,name="room 2")
    room_id2 = room2["id"]
    join_room(client=client,auth_headers=auth_headers2,room_id=room_id1)
    with client.websocket_connect(f"/api/v1/ws/user/id/{user_id1}/room/id/{room_id1}/") as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/user/id/{user_id2}/room/id/{room_id1}/") as websocket2:
            websocket1.send_text("user 1, room 1")
            assert websocket1.receive_text() == "user 1, room 1"
            assert websocket2.receive_text() == "user 1, room 1"
            websocket2.send_text("user 2, room 1")
            assert websocket2.receive_text() == "user 2, room 1"
            assert websocket1.receive_text() == "user 2, room 1"

    with client.websocket_connect(f"/api/v1/ws/user/id/{user_id2}/room/id/{room_id2}/") as websocket:
        websocket.send_text("user 2, room 2")
        assert websocket.receive_text() == "user 2, room 2"
    join_room(client=client,auth_headers=auth_headers1,room_id=room_id2)
    with client.websocket_connect(f"/api/v1/ws/user/id/{user_id1}/room/id/{room_id2}/") as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/user/id/{user_id2}/room/id/{room_id2}/") as websocket2:
            websocket1.send_text("user 1, room 2")
            assert websocket1.receive_text() == "user 1, room 2"
            assert websocket2.receive_text() == "user 1, room 2"
            websocket2.send_text("user 2, room 2")
            assert websocket1.receive_text() == "user 2, room 2"
            assert websocket2.receive_text() == "user 2, room 2"