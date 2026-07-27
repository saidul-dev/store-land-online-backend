def test_register_and_login(client):
    response = client.post("/api/v1/register", json={"email": "test@example.com", "password": "testpass123"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    response = client.post(
        "/api/v1/login", data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate_email_fails(client):
    client.post("/api/v1/register", json={"email": "dup@example.com", "password": "testpass123"})
    response = client.post("/api/v1/register", json={"email": "dup@example.com", "password": "testpass123"})
    assert response.status_code == 400


def _register_and_login(client, email, password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_name_requires_no_password(client):
    headers = _register_and_login(client, "nameuser@example.com")
    response = client.patch("/api/v1/me", json={"name": "Ada"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["user"]["name"] == "Ada"


def test_change_password_requires_current_password(client):
    headers = _register_and_login(client, "pwuser@example.com")

    wrong = client.patch(
        "/api/v1/me", json={"new_password": "newpass456", "current_password": "wrongpass"}, headers=headers
    )
    assert wrong.status_code == 400

    correct = client.patch(
        "/api/v1/me", json={"new_password": "newpass456", "current_password": "testpass123"}, headers=headers
    )
    assert correct.status_code == 200
    new_access_token = correct.json()["tokens"]["access_token"]

    login_with_new = client.post(
        "/api/v1/login", data={"username": "pwuser@example.com", "password": "newpass456"}
    )
    assert login_with_new.status_code == 200

    # The reissued access token from the PATCH response should also work immediately.
    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert me.status_code == 200


def test_change_email_reissues_a_working_token(client):
    headers = _register_and_login(client, "oldemail@example.com")

    response = client.patch(
        "/api/v1/me",
        json={"email": "newemail@example.com", "current_password": "testpass123"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "newemail@example.com"

    new_access_token = response.json()["tokens"]["access_token"]
    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "newemail@example.com"


def test_change_email_to_existing_address_rejected(client):
    _register_and_login(client, "taken@example.com")
    headers = _register_and_login(client, "wantstaken@example.com")

    response = client.patch(
        "/api/v1/me",
        json={"email": "taken@example.com", "current_password": "testpass123"},
        headers=headers,
    )
    assert response.status_code == 400


def test_email_change_without_current_password_rejected(client):
    headers = _register_and_login(client, "nopassword@example.com")
    response = client.patch("/api/v1/me", json={"email": "sneaky@example.com"}, headers=headers)
    assert response.status_code == 400
