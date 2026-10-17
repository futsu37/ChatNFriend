from fastapi.testclient import TestClient

from .utils.post import create_post
from .utils.user import create_and_auth_user, get_user_me

name = "test"
password = "testtest"

post_title = "title1"
post_desc = "description1"
def test_create_post(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    post = create_post(client=client,auth_headers=superuser_auth_headers,title="title_SU",desc="description_SU")

    super_user = get_user_me(client=client,auth_headers=superuser_auth_headers)
    
    SU_id = super_user["id"]
    
    assert SU_id == post["owner_id"]


    response_get = client.get("/api/v1/posts",headers=auth_headers)
    
    assert response_get.status_code == 200
    assert response_get.json()["count"] == 0
    
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)

    response_get = client.get("/api/v1/posts",headers=auth_headers)
    
    assert response_get.status_code == 200
    assert response_get.json()["count"] == 1

    user = get_user_me(client=client,auth_headers=auth_headers,username=name)
    
    user_id = user["id"]
    assert user_id == post["owner_id"]

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
    
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)
    
    post_id = post["id"]
    
    post_SU = create_post(client=client,auth_headers=superuser_auth_headers,title="title_SU",desc="description_SU")
    superuser_post_id = post_SU["id"]

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
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)
    post_id = post["id"]
    
    post_SU = create_post(client=client,auth_headers=superuser_auth_headers,title="title_SU",desc="description_SU")
    superuser_post_id = post_SU["id"]

    response_update = client.patch(
        f"/api/v1/posts/id/{superuser_post_id}",
        headers=auth_headers)    
    assert response_update.status_code == 403
    super_user = get_user_me(client=client, auth_headers=superuser_auth_headers)
    superuser_id = super_user["id"]

    response_update = client.patch(
        f"/api/v1/posts/id/{post_id}",
        headers=superuser_auth_headers,
        json={"owner_id": superuser_id}
    )
    assert response_update.status_code == 200
    assert response_update.json()["owner_id"] == superuser_id


