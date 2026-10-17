from fastapi.testclient import TestClient

from .utils.comment import create_comment
from .utils.post import create_post
from .utils.user import create_and_auth_user

name = "test"
password = "testtest"

post_title = "title1"
post_desc = "description1"

post_comment = "comment_test"
def test_create_comment(client: TestClient) -> None:
    auth_headers = create_and_auth_user(client=client,name=name,password=password)
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)
    post_id = post["id"]
    create_comment(client=client,auth_headers=auth_headers,post_id=post_id,post_comment=post_comment)

def test_update_comment(client: TestClient, superuser_auth_headers: dict[str,str]) -> None:
    auth_headers = create_and_auth_user(client=client,name="test",password="testtest")
    
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)
    post_id = post["id"]
    comment = create_comment(client=client,auth_headers=auth_headers,post_id=post_id,post_comment=post_comment)
    comment_id = comment["id"]

    comment_SU = create_comment(client=client,auth_headers=superuser_auth_headers,post_id=post_id,post_comment="comment_test_SU")
    comment_id_SU = comment_SU["id"]
    
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
    post = create_post(client=client,auth_headers=auth_headers,title=post_title,desc=post_desc)
    post_id = post["id"]
    comment = create_comment(client=client,auth_headers=auth_headers,post_id=post_id,post_comment=post_comment)
    comment_id = comment["id"]

    comment_SU = create_comment(client=client,auth_headers=superuser_auth_headers,post_id=post_id,post_comment="comment_test_SU")
    comment_id_SU = comment_SU["id"]

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
