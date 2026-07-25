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


def test_owner_can_create_category(client):
    headers = _register_and_login(client, "cowner@example.com")
    store_id = _create_store(client, headers, "catstore")

    response = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "electronics"


def test_categories_are_publicly_listable(client):
    headers = _register_and_login(client, "cowner2@example.com")
    store_id = _create_store(client, headers, "catlist")
    client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    )

    response = client.get(f"/api/v1/stores/{store_id}/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_subcategory_with_parent(client):
    headers = _register_and_login(client, "cowner3@example.com")
    store_id = _create_store(client, headers, "subcat")
    parent_id = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    ).json()["id"]

    response = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Mobiles", "slug": "mobiles", "parent_id": parent_id},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["parent_id"] == parent_id


def test_invalid_parent_rejected(client):
    headers = _register_and_login(client, "cowner4@example.com")
    store_id = _create_store(client, headers, "badparent")

    response = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Mobiles", "slug": "mobiles", "parent_id": 999999},
        headers=headers,
    )
    assert response.status_code == 404


def test_duplicate_slug_rejected(client):
    headers = _register_and_login(client, "cowner5@example.com")
    store_id = _create_store(client, headers, "dupslug")
    client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    )

    response = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics Again", "slug": "electronics"},
        headers=headers,
    )
    assert response.status_code == 400


def test_update_and_delete_category(client):
    headers = _register_and_login(client, "cowner6@example.com")
    store_id = _create_store(client, headers, "catupdate")
    category_id = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    ).json()["id"]

    update_response = client.put(
        f"/api/v1/stores/{store_id}/categories/{category_id}",
        json={"name": "Gadgets"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Gadgets"

    delete_response = client.delete(
        f"/api/v1/stores/{store_id}/categories/{category_id}", headers=headers
    )
    assert delete_response.status_code == 204


def test_create_category_requires_permission(client):
    owner_headers = _register_and_login(client, "cowner7@example.com")
    outsider_headers = _register_and_login(client, "coutsider@example.com")
    store_id = _create_store(client, owner_headers, "catperm")

    response = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=outsider_headers,
    )
    assert response.status_code == 404
