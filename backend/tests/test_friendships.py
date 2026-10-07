from backend.models.friendship import Status
from fastapi.testclient import TestClient

from .utils.user import create_and_auth_user

name = "test"
password = "testtest"
def test_friendship_send(client: TestClient) -> None:

    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)

    response_get_me = client.get(
            "/api/v1/users/me",
            headers=auth_headers1
        )
    assert response_get_me.status_code == 200
    assert "id" in response_get_me.json()
    user1_id = response_get_me.json()["id"]
    print(user1_id)

    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)

    response_get_me = client.get(
            "/api/v1/users/me",
            headers=auth_headers2
        )
    assert response_get_me.status_code == 200
    assert "id" in response_get_me.json()
    user2_id = response_get_me.json()["id"]

    response_friendship_send = client.post(
        f"/api/v1/friendships/send/id/{user2_id}",
        headers=auth_headers2)
    assert response_friendship_send.status_code == 403

    response_friendship_send = client.post(
        f"/api/v1/friendships/send/id/{user1_id}",
        headers=auth_headers2)
    print(response_friendship_send)
    print(response_friendship_send.json())
    assert response_friendship_send.status_code == 200

    response_friendship_send = client.post(
            f"/api/v1/friendships/send/id/{user1_id}",
            headers=auth_headers2)
    assert response_friendship_send.status_code == 403

    response_friendship_get = client.get(
        "/api/v1/friendships/",headers=auth_headers2)

    assert response_friendship_get.status_code == 200
    assert "count" in response_friendship_get.json()
    assert response_friendship_get.json()["count"] == 1


    response_friendship_get = client.get(
        "/api/v1/friendships/",headers=auth_headers1)

    assert response_friendship_get.status_code == 200
    assert "count" in response_friendship_get.json()
    assert response_friendship_get.json()["count"] == 1

def test_accept_and_delete_friendship(client: TestClient) -> None:
    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)

    response_get_me = client.get(
            "/api/v1/users/me",
            headers=auth_headers1
        )
    assert response_get_me.status_code == 200
    assert "id" in response_get_me.json()
    user1_id = response_get_me.json()["id"]

    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)

    response_get_me = client.get(
            "/api/v1/users/me",
            headers=auth_headers2
        )
    assert response_get_me.status_code == 200
    assert "id" in response_get_me.json()
    user2_id = response_get_me.json()["id"]

    response_friendship_send = client.post(
        f"/api/v1/friendships/send/id/{user1_id}",
        headers=auth_headers2)
    assert response_friendship_send.status_code == 200
    assert "id" in response_friendship_send.json()
    assert "status" in response_friendship_send.json()
    assert response_friendship_send.json()["status"] == Status.PENDING
    friendship_id = response_friendship_send.json()["id"]

    response_friendship_accept = client.patch(
        f"/api/v1/friendships/accept/id/{friendship_id}",
        headers=auth_headers1)

    assert response_friendship_accept.status_code == 200
    assert "status" in response_friendship_accept.json()
    assert response_friendship_accept.json()["status"] == Status.ACCEPTED

    response_friendship_accept = client.patch(
            f"/api/v1/friendships/accept/id/{friendship_id}",
            headers=auth_headers1)

    assert response_friendship_accept.status_code == 400

    response_friendship_get = client.get(
        f"/api/v1/friendships/friends/id/{user2_id}",
        headers=auth_headers1)

    assert response_friendship_get.status_code == 200
    assert "status" in response_friendship_get.json()["data"][0]
    assert response_friendship_get.json()["data"][0]["status"] == Status.ACCEPTED

    response_delete_friendship = client.delete(
        f"/api/v1/friendships/remove/id/{friendship_id}",
        headers=auth_headers1)
    
    assert response_delete_friendship.status_code == 200

    response_friendship_get = client.get(
        f"/api/v1/friendships/friends/id/{user1_id}",
        headers=auth_headers2)

    assert response_friendship_get.status_code == 200
    assert "count" in response_friendship_get.json()
    assert response_friendship_get.json()["count"] == 0

    
