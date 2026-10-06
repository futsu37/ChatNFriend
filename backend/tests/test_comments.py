from fastapi.testclient import TestClient

from .utils.user import create_and_auth_user


def test_create_comment(client: TestClient) -> None:
    auth_headers = create_and_auth_user(client=client,name="test",password="testtest")
    response_post_create = client.post(
        "/api/v1/posts/",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})
    
    assert response_post_create.status_code == 200
    assert "id" in response_post_create.json()
    post_id = response_post_create.json()["id"]
    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=auth_headers,
        json={"content":"comment_test"}
    )
    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == "comment_test"

def test_update_comment(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name="test",password="testtest")
    response_post_create = client.post(
        "/api/v1/posts/",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})
    
    assert response_post_create.status_code == 200
    assert "id" in response_post_create.json()
    post_id = response_post_create.json()["id"]
    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=auth_headers,
        json={"content":"comment_test"}
    )
    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == "comment_test"
    assert "post_id" in response_comment_create.json()
    assert "id" in response_comment_create.json()
    comment_id = response_comment_create.json()["id"]

    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=superuser_auth_headers,
        json={"content":"comment_test_SU"}
    )

    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == "comment_test_SU"
    assert "post_id" in response_comment_create.json()
    assert "id" in response_comment_create.json()
    comment_id_SU = response_comment_create.json()["id"]
    
    response_comment_update = client.patch(
        f"/api/v1/comments/id/{comment_id_SU}",
        headers=auth_headers,
        json={}
    )
    assert response_comment_update.status_code == 403
    
    response_comment_update = client.patch(
        f"/api/v1/comments/id/{comment_id}",
        headers=superuser_auth_headers,
        json={"content":"updated_content"}
    )
    assert response_comment_update.status_code == 200
    assert response_comment_update.json()["content"] == "updated_content"

def test_delete_comment(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name="test",password="testtest")
    response_post_create = client.post(
        "/api/v1/posts/",
        headers=auth_headers,
        json={"title":"title1","description":"description1"})
    
    assert response_post_create.status_code == 200
    assert "id" in response_post_create.json()
    post_id = response_post_create.json()["id"]
    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=auth_headers,
        json={"content":"comment_test"}
    )
    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == "comment_test"
    assert "post_id" in response_comment_create.json()
    assert "id" in response_comment_create.json()
    comment_id = response_comment_create.json()["id"]

    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=superuser_auth_headers,
        json={"content":"comment_test_SU"}
    )

    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == "comment_test_SU"
    assert "post_id" in response_comment_create.json()
    assert "id" in response_comment_create.json()
    comment_id_SU = response_comment_create.json()["id"]

    response_delete = client.delete(
        f"/api/v1/comments/id/{comment_id_SU}",
        headers=auth_headers)

    assert response_delete.status_code == 403
    
    response_delete = client.delete(
        f"/api/v1/comments/id/{comment_id_SU}",
        headers=superuser_auth_headers)
    
    assert response_delete.status_code == 200

    response_delete = client.delete(
        f"/api/v1/comments/id/{comment_id}",
        headers=superuser_auth_headers)
    
    assert response_delete.status_code == 200
