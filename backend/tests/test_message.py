from fastapi.testclient import TestClient

from .utils.message import delete_message, get_message, update_message
from .utils.room import create_room, send_message
from .utils.user import create_and_auth_user, get_user_me

name = "test"
password="testtest"

room_name="room_test"
message_content="message_test"
updated_message="updated_message"
def test_get_message(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    user_sender = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_sender_id = user_sender["id"] 
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]

    message = send_message(client=client,auth_headers=auth_headers, room_id=room_id, message=message_content)
    message_id = message["id"]

    get_message(
        client=client,
        superuser_auth_headers=superuser_auth_headers,
        sender_id=user_sender_id, 
        room_id=room_id, 
        message_id=message_id,
        message_content=message_content)

    get_message_response = client.get(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers)
    assert get_message_response.status_code == 403
    
def test_redact_message(client: TestClient, superuser_auth_headers: dict[str,str]):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    user_sender = get_user_me(client=client,auth_headers=auth_headers,username=name)
    user_sender_id = user_sender["id"] 
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]

    message = send_message(client=client,auth_headers=auth_headers, room_id=room_id, message=message_content)
    message_id = message["id"]

    update_message(client=client,auth_headers=auth_headers,message_id=message_id,updated_message=updated_message)
    
    get_message(
        client=client,
        superuser_auth_headers=superuser_auth_headers,
        sender_id=user_sender_id, 
        room_id=room_id, 
        message_id=message_id,
        message_content=updated_message)

    message_update_response = client.patch(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers2,
        json={"content":"Updated by non-creator"})

    assert message_update_response.status_code == 403

    get_message(
        client=client,
        superuser_auth_headers=superuser_auth_headers,
        sender_id=user_sender_id, 
        room_id=room_id, 
        message_id=message_id,
        message_content=updated_message)
    
    update_message(client=client,auth_headers=superuser_auth_headers,message_id=message_id,updated_message="Updated by super user")

    get_message(
        client=client,
        superuser_auth_headers=superuser_auth_headers,
        sender_id=user_sender_id, 
        room_id=room_id, 
        message_id=message_id,
        message_content="Updated by super user")

def test_delete_message(client: TestClient, superuser_auth_headers: dict[str,str]):
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    room = create_room(client=client,auth_headers=auth_headers,name=room_name)
    room_id = room["id"]

    message = send_message(client=client,auth_headers=auth_headers, room_id=room_id, message=message_content)
    message_id = message["id"]

    delete_message_response = client.delete(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers2)
    assert delete_message_response.status_code == 403

    get_message_response = client.get(
        f"/api/v1/messages/id/{message_id}",
        headers=superuser_auth_headers)
    assert get_message_response.status_code == 200

    delete_message(client=client, auth_headers=auth_headers,message_id=message_id)
    
    get_message_response = client.get(
        f"/api/v1/messages/id/{message_id}",
        headers=superuser_auth_headers)
    assert get_message_response.status_code == 404

    message = send_message(client=client,auth_headers=auth_headers, room_id=room_id, message=message_content)
    message_id = message["id"]

    delete_message(client=client, auth_headers=superuser_auth_headers,message_id=message_id)

    get_message_response = client.get(
        f"/api/v1/messages/id/{message_id}",
        headers=superuser_auth_headers)
    assert get_message_response.status_code == 404