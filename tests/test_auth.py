def test_register_and_login(client):
    response = client.post("/register", json={"email": "test@example.com", "password": "testpass123"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    response = client.post(
        "/login", data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate_email_fails(client):
    client.post("/register", json={"email": "dup@example.com", "password": "testpass123"})
    response = client.post("/register", json={"email": "dup@example.com", "password": "testpass123"})
    assert response.status_code == 400
