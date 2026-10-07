from collections.abc import Iterator

import pytest
from backend.api.deps import get_db
from backend.core.config import settings
from backend.core.database import init_db
from backend.main import app
from backend.models import Comment, Friendship, Post, User  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def client() -> Iterator[TestClient]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def get_test_db() -> Iterator[Session]:
        with Session(test_engine) as session:
            init_db(session)
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = get_test_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        SQLModel.metadata.drop_all(test_engine)
        test_engine.dispose()

@pytest.fixture
def superuser_auth_headers(client: TestClient) -> dict[str,str]:
    response = client.post(
        "/api/v1/login/access-token",
        data={
        "username": settings.FIRST_SUPERUSER_USERNAME, 
        "password":settings.FIRST_SUPERUSER_PASSWORD}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    access_token = response.json()["access_token"]
    token_type = response.json()["token_type"]
    auth_headers = {"Authorization":f"{token_type} {access_token}"}
    return auth_headers
    
