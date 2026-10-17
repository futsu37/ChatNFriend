from backend.models.friendship import Status
from fastapi.testclient import TestClient

from .utils.friendship import get_friendships
from .utils.user import create_and_auth_user, get_user_me

name = "test"
password = "testtest"
def test_friendship_send(client: TestClient) -> None:

    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)
    user1 = get_user_me(client=client,auth_headers=auth_headers1,username="user1")
    user1_id = user1["id"]

    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    user2 = get_user_me(client=client,auth_headers=auth_headers2,username="user2")
    user2_id = user2["id"]

    response_friendship_send = client.post(
        f"/api/v1/friendships/send/id/{user2_id}",
        headers=auth_headers2)
    assert response_friendship_send.status_code == 403

    response_friendship_send = client.post(
        f"/api/v1/friendships/send/id/{user1_id}",
        headers=auth_headers2)

    assert response_friendship_send.status_code == 200

    response_friendship_send = client.post(
            f"/api/v1/friendships/send/id/{user1_id}",
            headers=auth_headers2)
    assert response_friendship_send.status_code == 403
    
    friendship = get_friendships(client=client,auth_headers=auth_headers2)
    assert friendship["count"] == 1

    friendship = get_friendships(client=client,auth_headers=auth_headers1)
    assert friendship["count"] == 1

def test_accept_and_delete_friendship(client: TestClient) -> None:
    auth_headers1 = create_and_auth_user(client=client,name="user1",password=password)
    user1 = get_user_me(client=client,auth_headers=auth_headers1,username="user1")
    user1_id = user1["id"]

    auth_headers2 = create_and_auth_user(client=client,name="user2",password=password)
    get_user_me(client=client,auth_headers=auth_headers2,username="user2")

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

    friendship = get_friendships(client=client,auth_headers=auth_headers1)

    assert "status" in friendship["data"][0]
    assert friendship["data"][0]["status"] == Status.ACCEPTED

    response_delete_friendship = client.delete(
        f"/api/v1/friendships/remove/id/{friendship_id}",
        headers=auth_headers1)
    
    assert response_delete_friendship.status_code == 200

    friendship = get_friendships(client=client,auth_headers=auth_headers1)
    assert friendship["count"] == 0

    
