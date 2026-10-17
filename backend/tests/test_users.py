from fastapi.testclient import TestClient

from .utils.user import create_and_auth_user, get_user_me

name = "test"
password = "testtest"

def test_signup_creates_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/signup",
        json={"username": "alice", "password": "test-password"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "hashed_password" not in response.json()

    lookup_response = client.get("/api/v1/users/username/alice")

    assert lookup_response.status_code == 200
    assert lookup_response.json()["username"] == "alice"

def test_delete_user(client: TestClient) -> None:
    auth_headers = create_and_auth_user(
        client=client,
        name=name,
        password=password)
    
    get_user_me(client=client,auth_headers=auth_headers,username=name)

    response_delete = client.delete(
        "/api/v1/users/me",headers=auth_headers)

    assert response_delete.status_code == 200
    assert response_delete.json() == "User was successfully deleted"
    
    response_get_me = client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response_get_me.status_code == 404

def test_update_user(client: TestClient) -> None:

    auth_headers = create_and_auth_user(
        client=client,
        name=name,
        password=password)

    get_user_me(client=client,auth_headers=auth_headers,username=name)

    response_update = client.patch(
        "/api/v1/users/me", 
        json={"username": "test2"},
        headers=auth_headers)
    assert response_update.status_code == 200
    assert response_update.json()["username"] == "test2"

    get_user_me(client=client,auth_headers=auth_headers,username="test2")


def test_read_users_superuser(
    client: TestClient, 
    superuser_auth_headers: dict[str,str]) -> None:
    response = client.get(
        "/api/v1/users/",
        headers=superuser_auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] == 1

    auth_headers = create_and_auth_user(
        client=client,
        name=name,
        password=password)

    response = client.get(
        "/api/v1/users",
        headers=auth_headers)

    assert response.status_code == 403

def test_update_superuser(
    client: TestClient, 
    superuser_auth_headers: dict[str,str]) -> None:

    response_create = client.post(
        "/api/v1/users/signup",
        json={"username": f"{name}", "password": f"{password}"},
    )
    assert response_create.status_code == 200
    assert response_create.json()["username"] == name
    assert "id" in response_create.json()

    user_id = response_create.json()["id"]
    response_update = client.patch(
        f"/api/v1/users/id/{user_id}",
        headers=superuser_auth_headers,
        json={"username":"test2"})
        
    assert response_update.status_code == 200

    response_get = client.get(
        f"/api/v1/users/id/{user_id}")

    assert response_get.status_code == 200
    assert response_get.json()["username"] == "test2"
def test_delete_superuser(
    client: TestClient, 
    superuser_auth_headers: dict[str,str]) -> None:
    response_create = client.post(
        "/api/v1/users/signup",
        json={"username": f"{name}", "password": f"{password}"},
    )
    assert response_create.status_code == 200
    assert response_create.json()["username"] == name
    assert "id" in response_create.json()

    user_id = response_create.json()["id"]
    response_delete = client.delete(
        f"/api/v1/users/id/{user_id}",
        headers=superuser_auth_headers)

    assert response_delete.status_code == 200
    assert response_delete.json() == "User was successfully deleted"

    response_get = client.get(
        f"/api/v1/users/id/{user_id}")
    assert response_get.status_code == 404

    response_delete_me = client.delete(
        "/api/v1/users/me",
        headers=superuser_auth_headers
    )
    assert response_delete_me.status_code == 403
    assert response_delete_me.json()["detail"] == "Super users are not allowed to delete themselves"

