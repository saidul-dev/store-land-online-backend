def _register_and_login(client, email, password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    return response.json()


def test_login_returns_access_and_refresh_token(client):
    tokens = _register_and_login(client, "ruser@example.com")
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["access_token"] != tokens["refresh_token"]


def test_refresh_issues_new_token_pair_and_new_access_token_works(client):
    tokens = _register_and_login(client, "ruser2@example.com")

    response = client.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    me_response = client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {new_tokens['access_token']}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ruser2@example.com"


def test_rotated_refresh_token_cannot_be_reused(client):
    tokens = _register_and_login(client, "ruser3@example.com")
    client.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})

    replay_response = client.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert replay_response.status_code == 401


def test_invalid_refresh_token_rejected(client):
    response = client.post("/api/v1/refresh", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401


def test_logout_revokes_refresh_token(client):
    tokens = _register_and_login(client, "ruser4@example.com")

    logout_response = client.post("/api/v1/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_response.status_code == 204

    refresh_response = client.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 401


def test_logout_with_unknown_token_is_a_no_op(client):
    response = client.post("/api/v1/logout", json={"refresh_token": "already-gone"})
    assert response.status_code == 204
