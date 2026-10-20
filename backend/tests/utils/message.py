from fastapi.testclient import TestClient


def get_message(
    *,
    client: TestClient, 
    superuser_auth_headers: dict[str,str], 
    room_id: str, 
    sender_id: str,
    message_id: str,
    message_content: str):
    get_message_response = client.get(
        f"/api/v1/messages/id/{message_id}",
        headers=superuser_auth_headers)

    assert get_message_response.status_code == 200
    assert "content" in get_message_response.json()
    assert "room_id" in get_message_response.json()
    assert "sender_id" in get_message_response.json()
    assert get_message_response.json()["content"] == message_content
    assert get_message_response.json()["room_id"] == room_id
    assert get_message_response.json()["sender_id"] == sender_id
    return get_message_response.json()

def update_message(*,
    client: TestClient,
    auth_headers: dict[str,str], 
    message_id: str,
    updated_message: str):
    message_update_response = client.patch(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers,
        json={"content":""})

    assert message_update_response.status_code == 422

    message_update_response = client.patch(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers,
        json={"content":updated_message})
    assert message_update_response.status_code == 200
    message = message_update_response.json()
    assert message["content"] == updated_message
    return message

def delete_message(*,client:TestClient,auth_headers:dict[str,str] ,message_id: str):
    delete_message_response = client.delete(
        f"/api/v1/messages/id/{message_id}",
        headers=auth_headers)
    assert delete_message_response.status_code == 200