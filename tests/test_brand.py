def _register_and_login(client, email, password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_store(client, headers, subdomain):
    response = client.post(
        "/api/v1/stores/", json={"name": "Test Store", "subdomain": subdomain}, headers=headers
    )
    return response.json()["id"]


def test_owner_can_create_brand(client):
    headers = _register_and_login(client, "bowner@example.com")
    store_id = _create_store(client, headers, "brandstore")

    response = client.post(
        f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme", "slug": "acme"}, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "acme"


def test_brands_are_publicly_listable(client):
    headers = _register_and_login(client, "bowner2@example.com")
    store_id = _create_store(client, headers, "brandlist")
    client.post(f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme", "slug": "acme"}, headers=headers)

    response = client.get(f"/api/v1/stores/{store_id}/brands/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_slug_rejected(client):
    headers = _register_and_login(client, "bowner3@example.com")
    store_id = _create_store(client, headers, "branddup")
    client.post(f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme", "slug": "acme"}, headers=headers)

    response = client.post(
        f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme Again", "slug": "acme"}, headers=headers
    )
    assert response.status_code == 400


def test_update_and_delete_brand(client):
    headers = _register_and_login(client, "bowner4@example.com")
    store_id = _create_store(client, headers, "brandupdate")
    brand_id = client.post(
        f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme", "slug": "acme"}, headers=headers
    ).json()["id"]

    update_response = client.put(
        f"/api/v1/stores/{store_id}/brands/{brand_id}", json={"name": "Acme Corp"}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Acme Corp"

    delete_response = client.delete(f"/api/v1/stores/{store_id}/brands/{brand_id}", headers=headers)
    assert delete_response.status_code == 204


def test_create_brand_requires_permission(client):
    owner_headers = _register_and_login(client, "bowner5@example.com")
    outsider_headers = _register_and_login(client, "boutsider@example.com")
    store_id = _create_store(client, owner_headers, "brandperm")

    response = client.post(
        f"/api/v1/stores/{store_id}/brands/",
        json={"name": "Acme", "slug": "acme"},
        headers=outsider_headers,
    )
    assert response.status_code == 404
