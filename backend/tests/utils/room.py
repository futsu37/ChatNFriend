

from fastapi.testclient import TestClient


def create_room(*,client:TestClient, auth_headers: dict[str,str], name: str):
    response = client.post(
        "/api/v1/rooms",
        headers=auth_headers,
        json={"name": name})

    assert response.status_code == 200
    assert "name" in response.json()
    assert "id" in response.json()
    assert response.json()["name"] == name
    assert response.json()["users_in"].__len__() == 1
    return response.json()

def join_room(*,client:TestClient, auth_headers: dict[str,str], room_id: str):
    response_join = client.post(f"/api/v1/rooms/join/id/{room_id}",headers=auth_headers)

    assert response_join.status_code == 200
    assert "room_id" in response_join.json()
    assert response_join.json()["room_id"] == room_id

    response_join = client.post(f"/api/v1/rooms/join/id/{room_id}",headers=auth_headers)

    assert response_join.status_code == 403
    return response_join.json()

def send_message(*,client:TestClient, auth_headers: dict[str,str], room_id: str, message: str):
    response_send_message = client.post(
        f"api/v1/rooms/message/id/{room_id}",
        headers=auth_headers,
        json={"content": message})
    assert response_send_message.status_code == 200
    assert response_send_message.json()["content"] == message
    return response_send_message.json()

def get_room_messages(*,client:TestClient, auth_headers: dict[str,str], room_id: str):
    response_get_room_messages = client.get(
        f"/api/v1/rooms/messages/id/{room_id}",
        headers=auth_headers)
    
    assert response_get_room_messages.status_code == 200
    assert "count" in response_get_room_messages.json()
    assert "data" in response_get_room_messages.json()
    return response_get_room_messages.json()

def get_room(*,client:TestClient, auth_headers: dict[str,str], room_id: str):
    response = client.get(f"/api/v1/rooms/id/{room_id}",headers=auth_headers)
    assert response.status_code == 200
    assert "users_in" in response.json()
    return response.json()

def leave_room(*,client:TestClient, auth_headers: dict[str,str], room_id: str):
    response_room_leave = client.delete(f"/api/v1/rooms/leave/id/{room_id}",headers=auth_headers)
    assert response_room_leave.status_code == 200
    

def kick_user(*,client:TestClient, superuser_auth_headers: dict[str,str], room_id: str, user_id: str):
    response_kick_user = client.delete(
        f"/api/v1/rooms/id/{room_id}/users/id/{user_id}",
        headers=superuser_auth_headers)
    
    assert response_kick_user.status_code == 200

    response_kick_user = client.delete(
        f"/api/v1/rooms/id/{room_id}/users/id/{user_id}",
        headers=superuser_auth_headers)
    
    assert response_kick_user.status_code == 404
def delete_room(*,client:TestClient, superuser_auth_headers: dict[str,str], room_id: str):
    response_delete_room = client.delete(
        f"api/v1/rooms/id/{room_id}"
        ,headers=superuser_auth_headers)
    
    assert response_delete_room.status_code == 200
