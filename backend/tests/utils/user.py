def create_and_auth_user(*,client, name: str, password: str):
    response_create = client.post(
        "/api/v1/users/signup",
        json={"username": f"{name}", "password": f"{password}"},
    )

    assert response_create.status_code == 200
    assert response_create.json()["username"] == name

    response_auth = client.post(
        "/api/v1/login/access-token",
        data={"username": f"{name}", "password": f"{password}"})

    assert response_auth.status_code == 200
    
    access_token = response_auth.json()["access_token"]
    token_type = response_auth.json()["token_type"]
    auth_headers = {"Authorization":f"{token_type} {access_token}"}
    return auth_headers

def get_user_me(*,client,auth_headers: dict[str,str], username: str | None = None):
    response_get_me = client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response_get_me.status_code == 200
    if username: 
        assert response_get_me.json()["username"] == username
    assert "id" in response_get_me.json()
    return response_get_me.json() 