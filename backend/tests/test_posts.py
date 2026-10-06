from fastapi.testclient import TestClient

from .utils.user import create_and_auth_user

name = "test"
password = "testtest"
def test_create_post(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    response_post = client.post(
        "/api/v1/posts",
        headers=superuser_auth_headers,
        json={"title":"title_SU","description":"description_SU"})
    assert response_post.status_code == 200
    assert "id" in response_post.json()
    assert "owner_id" in response_post.json()

    response_get_user_me = client.get("/api/v1/users/me",headers=superuser_auth_headers)
    
    assert response_get_user_me.status_code == 200
    assert "id" in response_get_user_me.json()
    
    SU_id = response_get_user_me.json()["id"]
    
    assert SU_id == response_post.json()["owner_id"]

    response_get = client.get("/api/v1/posts",headers=auth_headers)
    
    assert response_get.status_code == 200
    assert response_get.json()["count"] == 0
    

    response_post = client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})
    assert response_post.status_code == 200
    assert response_post.json()["title"] == "title1"
    assert response_post.json()["description"] == "description1"
    assert "id" in response_post.json()
    assert "owner_id" in response_post.json()

    response_get = client.get("/api/v1/posts",headers=auth_headers)
    
    assert response_get.status_code == 200
    assert response_get.json()["count"] == 1

    response_get_user_me = client.get("/api/v1/users/me",headers=auth_headers)
    
    assert response_get_user_me.status_code == 200
    assert "id" in response_get_user_me.json()
    user_id = response_get_user_me.json()["id"]
    assert user_id == response_post.json()["owner_id"]

    response_post = client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={"title":"","description":""})
    
    assert response_post.status_code == 422

    response_get = client.get("/api/v1/posts",headers=auth_headers)
    
    assert response_get.status_code == 200
    assert response_get.json()["count"] == 1

    response_get_superuser = client.get("/api/v1/posts",headers=superuser_auth_headers)
    
    assert response_get_superuser.status_code == 200
    assert response_get_superuser.json()["count"] == 2

def test_delete_post(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    response_post = client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})

    assert response_post.status_code == 200
    assert response_post.json()["title"] == "title1"
    assert response_post.json()["description"] == "description1"
    assert "id" in response_post.json()
    post_id = response_post.json()["id"]
    
    response_post_superuser = client.post(
        "/api/v1/posts",
        headers=superuser_auth_headers,
        json={"title":"title_SU","description":"description_SU"})
    
    assert response_post_superuser.status_code == 200
    assert response_post_superuser.json()["title"] == "title_SU"
    assert response_post_superuser.json()["description"] == "description_SU"
    assert "id" in response_post_superuser.json()
    superuser_post_id = response_post_superuser.json()["id"]

    response_delete = client.delete(
        f"/api/v1/posts/id/{superuser_post_id}",
        headers=auth_headers)
    
    assert response_delete.status_code == 403
    assert response_delete.json()["detail"] == "You can only delete your posts"

    response_delete = client.delete(
        f"/api/v1/posts/id/{post_id}",
        headers=superuser_auth_headers)
    
    assert response_delete.status_code == 200

    response_delete = client.delete(
        f"/api/v1/posts/id/{post_id}",
        headers=superuser_auth_headers)

    assert response_delete.status_code == 404

def test_update_post(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    response_post = client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})

    assert response_post.status_code == 200
    assert response_post.json()["title"] == "title1"
    assert response_post.json()["description"] == "description1"
    assert "id" in response_post.json()
    assert "owner_id" in response_post.json()
    post_id = response_post.json()["id"]
    
    response_post_superuser = client.post(
        "/api/v1/posts",
        headers=superuser_auth_headers,
        json={"title":"title_SU","description":"description_SU"})
    
    assert response_post_superuser.status_code == 200
    assert response_post_superuser.json()["title"] == "title_SU"
    assert response_post_superuser.json()["description"] == "description_SU"
    assert "id" in response_post_superuser.json()
    superuser_post_id = response_post_superuser.json()["id"]    

    response_update = client.patch(
        f"/api/v1/posts/id/{superuser_post_id}",
        headers=auth_headers)    
    assert response_update.status_code == 403
    
    response_user_get = client.get(
        "/api/v1/users/me",
        headers=superuser_auth_headers
    )

    assert response_user_get.status_code == 200
    assert "id" in response_user_get.json()
    superuser_id = response_user_get.json()["id"]

    response_update = client.patch(
        f"/api/v1/posts/id/{post_id}",
        headers=superuser_auth_headers,
        json={"owner_id": superuser_id}
    )
    assert response_update.status_code == 200
    assert response_update.json()["owner_id"] == superuser_id


