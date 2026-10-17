from fastapi.testclient import TestClient


def create_comment(*,client: TestClient, auth_headers: dict[str,str], post_id: str, post_comment: str):
    response_comment_create = client.post(
        f"/api/v1/posts/id/comment/{post_id}",
        headers=auth_headers,
        json={"content":post_comment}
    )
    assert response_comment_create.status_code == 200
    assert response_comment_create.json()["content"] == post_comment
    assert "post_id" in response_comment_create.json()
    assert "id" in response_comment_create.json()
    return response_comment_create.json()