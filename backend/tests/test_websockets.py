import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketDenialResponse
from starlette.websockets import WebSocketDisconnect

from .utils.room import create_room, get_room_messages, join_room, leave_room
from .utils.user import create_and_auth_user, get_user_me
from .utils.websocket import check_message_info

name = "test"
password = "testtest"

room_name = "Test Room"
message = "Test message"
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

def test_subprotocol_token(client: TestClient):
    auth_headers = create_and_auth_user(client=client, name=name, password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    token = auth_headers["Authorization"].split(" ", maxsplit=1)[1]

    with client.websocket_connect(
        f"/api/v1/ws/room/id/{room_id}/",
        subprotocols=["chat", f"access_token.{token}"],
    ) as websocket:
        assert websocket.accepted_subprotocol == "chat"
        websocket.send_text(persist_message)
        assert websocket.receive_json()["content"] == persist_message

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
            assert websocket1.receive_json()["content"] == "room 1"

            websocket2.send_text("room 2")
            assert websocket2.receive_json()["content"] == "room 2"

            websocket1.send_text("room 1 again")
            assert websocket1.receive_json()["content"] == "room 1 again"

persist_message = "persist_message_test"
def test_persist_message(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers) as websocket:
            websocket.send_text(persist_message)
            received_message = websocket.receive_json()
            assert "id" in received_message
            assert "created_at" in received_message
            assert "sender_id" in received_message
            assert "content" in received_message
            assert "room_id" in received_message
            assert received_message["sender_id"] == user_id 
            assert received_message["content"] == persist_message 
            assert received_message["room_id"] == room_id 
            message_id = received_message["id"]
    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)    
    assert "data" in messages
    assert messages["data"].__len__() == 1
    message = messages["data"][0]
    assert message["id"] == message_id
    assert message["content"] == persist_message
    assert message["sender_id"] == user_id

def test_persist_message_multiple_users(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    join_room(client=client,auth_headers=auth_headers2,room_id=room_id)
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers) as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers2) as websocket2:
                websocket1.send_text(persist_message)
                received_message1 = websocket1.receive_json()
                check_message_info(received_message1,user_id,room_id,persist_message)
                received_message2 = websocket2.receive_json()
                check_message_info(received_message2,user_id,room_id,persist_message)
                message_id = received_message1["id"]
    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)    
    assert "data" in messages
    assert messages["data"].__len__() == 1
    message = messages["data"][0]
    assert message["id"] == message_id
    assert message["content"] == persist_message
    assert message["sender_id"] == user_id

def test_message_updates_and_deletes_are_broadcast(client: TestClient):
    author_headers = create_and_auth_user(
        client=client,
        name="message_author",
        password=password,
    )
    reader_headers = create_and_auth_user(
        client=client,
        name="message_reader",
        password=password,
    )
    room = create_room(
        client=client,
        auth_headers=author_headers,
        name="message changes",
    )
    room_id = room["id"]
    join_room(client=client, auth_headers=reader_headers, room_id=room_id)

    with client.websocket_connect(
        f"/api/v1/ws/room/id/{room_id}/",
        headers=author_headers,
    ) as author_socket, client.websocket_connect(
        f"/api/v1/ws/room/id/{room_id}/",
        headers=reader_headers,
    ) as reader_socket:
        author_socket.send_text("before redaction")
        message = author_socket.receive_json()
        reader_socket.receive_json()

        redact_response = client.patch(
            f"/api/v1/messages/id/{message['id']}",
            headers=author_headers,
            json={"content": "after redaction"},
        )
        assert redact_response.status_code == 200
        expected_update = {
            "event": "message_updated",
            "message": redact_response.json(),
        }
        assert author_socket.receive_json() == expected_update
        assert reader_socket.receive_json() == expected_update

        delete_response = client.delete(
            f"/api/v1/messages/id/{message['id']}",
            headers=author_headers,
        )
        assert delete_response.status_code == 200
        expected_delete = {
            "event": "message_deleted",
            "room_id": room_id,
            "message_id": message["id"],
        }
        assert author_socket.receive_json() == expected_delete
        assert reader_socket.receive_json() == expected_delete

def test_connection_after_leaving_room(client: TestClient):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    join_room(client=client,auth_headers=auth_headers2,room_id=room_id)
    with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers) as websocket1:  # noqa: SIM117
        with client.websocket_connect(f"/api/v1/ws/room/id/{room_id}/",headers=auth_headers2) as websocket2:
                websocket1.send_text(persist_message)
                received_message1 = websocket1.receive_json()
                check_message_info(received_message1,user_id,room_id,persist_message)
                received_message2 = websocket2.receive_json()
                check_message_info(received_message2,user_id,room_id,persist_message)
                leave_room(client=client, auth_headers=auth_headers2,room_id=room_id)
                websocket1.send_text("message after leaving")
                with pytest.raises(WebSocketDisconnect) as exc:
                    websocket2.receive_json()
                assert exc.value.code == 1008
                received_message3 = websocket1.receive_json()
                check_message_info(received_message3,user_id,room_id,"message after leaving")