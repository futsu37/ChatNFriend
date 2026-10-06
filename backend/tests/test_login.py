from backend.core.config import settings
from fastapi.testclient import TestClient


def test_login_get_access_token(client: TestClient) -> None:
    response_create = client.post(
        "/api/v1/users/signup",
        json={"username":"test","password":"testtest"}
    )

    assert response_create.status_code == 200
    assert response_create.json()["username"] == "test"

    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test", "password":"testtest"}
    )
    assert response.status_code == 200

def test_login_superuser(client: TestClient) -> None:
    response = client.post(
        "/api/v1/login/access-token",
        data={
        "username": settings.FIRST_SUPERUSER_USERNAME, 
        "password":settings.FIRST_SUPERUSER_PASSWORD}
    )
    assert response.status_code == 200
