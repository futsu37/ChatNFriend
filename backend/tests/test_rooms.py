from fastapi.testclient import TestClient

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
from .utils.user import create_and_auth_user, get_user_me

name = "test"
password = "testtest"
room_name = "Test Room"
message = "Test message"
def test_create_room(client: TestClient) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)

    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]

    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]

    room = get_room(client=client,auth_headers=auth_headers,room_id=room_id)
    assert "user_id" in room["users_in"][0]
    assert room["users_in"][0]["user_id"] == user_id


def test_join_room(client: TestClient) -> None:
    auth_headers1 = create_and_auth_user(client=client,name="test1",password=password)
    auth_headers2 = create_and_auth_user(client=client,name="test2",password=password)

    user1 = get_user_me(client=client,auth_headers=auth_headers1,username="test1")
    user_id1 = user1["id"]

    user2 = get_user_me(client=client,auth_headers=auth_headers2,username="test2")
    user_id2 = user2["id"]

    room = create_room(client=client,auth_headers=auth_headers1,name=room_name)
    room_id = room["id"]

    join_room(client=client,auth_headers=auth_headers2,room_id=room_id)

    room = get_room(client=client,auth_headers=auth_headers2,room_id=room_id)
    assert "user_id" in room["users_in"][0]
    assert "user_id" in room["users_in"][1]
    user_id_data = {
        room["users_in"][0]["user_id"], 
        room["users_in"][1]["user_id"]}

    expected_data1 = {user_id1, user_id2}
    expected_data2 = {user_id2, user_id1}

    assert user_id_data.issubset(expected_data1) or user_id_data.issubset(expected_data2)

    leave_room(client=client,auth_headers=auth_headers1,room_id=room_id)
    room = get_room(client=client,auth_headers=auth_headers1,room_id=room_id)
    assert room["users_in"][0]["user_id"] == user_id2

def test_send_message(client: TestClient) -> None:
    auth_headers1 = create_and_auth_user(client=client,name="test1",password=password)
    auth_headers2 = create_and_auth_user(client=client,name="test2",password=password)

    user1 = get_user_me(client=client,auth_headers=auth_headers1,username="test1")
    get_user_me(client=client,auth_headers=auth_headers2,username="test2")
    user_id1 = user1["id"]

    room = create_room(client=client,auth_headers=auth_headers1,name=room_name)
    room_id = room["id"]

    join_room(client=client,auth_headers=auth_headers2,room_id=room_id)

    send_message(client=client,auth_headers=auth_headers1,room_id=room_id,message=message)

    room_messages = get_room_messages(client=client,auth_headers=auth_headers2,room_id=room_id)
    assert room_messages["count"] == 1
    assert room_messages["data"][0]["content"] == message
    assert room_messages["data"][0]["sender_id"] == user_id1

def test_kick_user(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    send_message(client=client,auth_headers=auth_headers,room_id=room_id,message=message)

    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)
    assert messages["count"] == 1
    assert messages["data"][0]["content"] == message
    assert messages["data"][0]["sender_id"] == user_id

    kick_user(client=client,superuser_auth_headers=superuser_auth_headers,room_id=room_id,user_id=user_id)

    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)
    
    assert messages["count"] == 1
    assert messages["data"][0]["content"] == message
    assert messages["data"][0]["sender_id"] == user_id

    room = get_room(client=client,auth_headers=auth_headers,room_id=room_id)
    assert room["users_in"].__len__() == 0

def test_delete_room(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    send_message(client=client,auth_headers=auth_headers,room_id=room_id,message=message)

    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)
    assert messages["count"] == 1
    assert messages["data"][0]["content"] == message
    assert messages["data"][0]["sender_id"] == user_id

    delete_room(client=client,superuser_auth_headers=superuser_auth_headers,room_id=room_id)
    
    response_get_room_messages = client.get(
        f"/api/v1/rooms/messages/id/{room_id}",
        headers=auth_headers)
    
    assert response_get_room_messages.status_code == 404

def test_leave_room(client: TestClient) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_id = user["id"]
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]
    send_message(client=client,auth_headers=auth_headers,room_id=room_id,message=message)

    messages = get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)
    assert messages["count"] == 1
    assert messages["data"][0]["content"] == message
    assert messages["data"][0]["sender_id"] == user_id

    leave_room(client=client,auth_headers=auth_headers,room_id=room_id)
    
    get_room_messages(client=client,auth_headers=auth_headers,room_id=room_id)
    
