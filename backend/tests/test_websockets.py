import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketDenialResponse

from .utils.room import (
    create_room,
    join_room,
)
from .utils.user import create_and_auth_user

name = "test"
password = "testtest"

room_name = "Test Room"
message = "Test message"
def test_room_message(client: TestClient):
    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    room1 = create_room(client=client,auth_headers=auth_headers1,name="room 1")
    room_id1 = room1["id"]
    room2 = create_room(client=client,auth_headers=auth_headers2,name="room 2")
    room_id2 = room2["id"]
    join_room(client=client,auth_headers=auth_headers2,room_id=room_id1)
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id1}/",headers=auth_headers1) as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id1}/",headers=auth_headers2) as websocket2:
            websocket1.send_text("user 1, room 1")
            assert websocket1.receive_text() == "user 1, room 1"
            assert websocket2.receive_text() == "user 1, room 1"
            websocket2.send_text("user 2, room 1")
            assert websocket2.receive_text() == "user 2, room 1"
            assert websocket1.receive_text() == "user 2, room 1"

    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id2}/",headers=auth_headers2) as websocket:
        websocket.send_text("user 2, room 2")
        assert websocket.receive_text() == "user 2, room 2"
    join_room(client=client,auth_headers=auth_headers1,room_id=room_id2)
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id2}/",headers=auth_headers1) as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id2}/",headers=auth_headers2) as websocket2:
            websocket1.send_text("user 1, room 2")
            assert websocket1.receive_text() == "user 1, room 2"
            assert websocket2.receive_text() == "user 1, room 2"
            websocket2.send_text("user 2, room 2")
            assert websocket1.receive_text() == "user 2, room 2"
            assert websocket2.receive_text() == "user 2, room 2"

dummy_headers = {"Authorization":"bearer 9iwajsdoif923kjjf9wjeufjiuewfj"}
def test_invalid_token(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    with pytest.raises(WebSocketDenialResponse) as exc:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=dummy_headers):
            pass
    assert exc.value.status_code == 403

def test_missing_token(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    with pytest.raises(WebSocketDenialResponse) as exc:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers={}):
            pass
    assert exc.value.status_code == 403

def test_not_a_room_member(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    
    auth_headers_outsider = create_and_auth_user(client=client,name="outsider",password=password)
    with pytest.raises(WebSocketDenialResponse) as exc:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers_outsider):
            pass
    assert exc.value.status_code == 404
        
def test_separate_room_message(client: TestClient):
    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    room1 = create_room(client=client,auth_headers=auth_headers1,name="room 1")
    room_id1 = room1["id"]
    room2 = create_room(client=client,auth_headers=auth_headers2,name="room 2")
    room_id2 = room2["id"]
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id1}/",headers=auth_headers1) as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id2}/",headers=auth_headers2) as websocket2:
            websocket1.send_text("room 1")
            assert websocket1.receive_text() == "room 1"

            websocket2.send_text("room 2")
            assert websocket2.receive_text() == "room 2"

            websocket1.send_text("room 1 again")
            assert websocket1.receive_text() == "room 1 again"
