def _register_and_login(client, email, password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_store(client):
    headers = _register_and_login(client, "owner@example.com")
    response = client.post(
        "/api/v1/stores/", json={"name": "Acme Shop", "subdomain": "acme"}, headers=headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["subdomain"] == "acme"
    assert body["domain_verified"] is False


def test_register_store_requires_auth(client):
    response = client.post("/api/v1/stores/", json={"name": "Acme Shop", "subdomain": "acme"})
    assert response.status_code == 401


def test_duplicate_subdomain_rejected(client):
    headers = _register_and_login(client, "owner2@example.com")
    client.post("/api/v1/stores/", json={"name": "Acme Shop", "subdomain": "dupe"}, headers=headers)
    response = client.post(
        "/api/v1/stores/", json={"name": "Another Shop", "subdomain": "dupe"}, headers=headers
    )
    assert response.status_code == 400


def test_reserved_subdomain_rejected(client):
    headers = _register_and_login(client, "owner3@example.com")
    response = client.post(
        "/api/v1/stores/", json={"name": "Admin Panel", "subdomain": "admin"}, headers=headers
    )
    assert response.status_code == 422


def test_resolve_store_by_subdomain(client):
    headers = _register_and_login(client, "owner4@example.com")
    client.post(
        "/api/v1/stores/", json={"name": "Resolve Me", "subdomain": "resolveme"}, headers=headers
    )

    response = client.get("/api/v1/stores/resolve", headers={"host": "resolveme.yourapp.com"})
    assert response.status_code == 200
    assert response.json()["subdomain"] == "resolveme"


def test_resolve_store_unknown_host_returns_404(client):
    response = client.get("/api/v1/stores/resolve", headers={"host": "doesnotexist.yourapp.com"})
    assert response.status_code == 404
