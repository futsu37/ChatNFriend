from fastapi.testclient import TestClient


def get_friendships(*,client: TestClient, auth_headers: dict[str,str]):
    response_friendship_get = client.get(
        "/api/v1/friendships/",headers=auth_headers)

    assert response_friendship_get.status_code == 200
    assert "count" in response_friendship_get.json()
    return response_friendship_get.json()