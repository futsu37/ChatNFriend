from fastapi.testclient import TestClient


def create_post(*,client: TestClient, auth_headers: dict[str,str],title:str, desc: str):
    response_post = client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={"title":title,"description":desc})
    assert response_post.status_code == 200
    assert "id" in response_post.json()
    assert "owner_id" in response_post.json()
    assert response_post.json()["title"] == title
    assert response_post.json()["description"] == desc
    return response_post.json()