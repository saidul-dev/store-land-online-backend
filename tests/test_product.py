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


def _create_product(client, headers, store_id, sku="SKU-1", price="19.99", stock=10):
    return client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Widget", "sku": sku, "price": price, "stock_quantity": stock},
        headers=headers,
    )


def test_owner_can_create_product(client):
    headers = _register_and_login(client, "powner@example.com")
    store_id = _create_store(client, headers, "productstore")

    response = _create_product(client, headers, store_id)
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "SKU-1"
    assert body["stock_quantity"] == 10


def test_products_are_publicly_listable(client):
    headers = _register_and_login(client, "powner2@example.com")
    store_id = _create_store(client, headers, "publicproducts")
    _create_product(client, headers, store_id)

    response = client.get(f"/api/v1/stores/{store_id}/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_product_requires_membership(client):
    owner_headers = _register_and_login(client, "powner3@example.com")
    outsider_headers = _register_and_login(client, "poutsider@example.com")
    store_id = _create_store(client, owner_headers, "membershipcheck")

    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Widget", "sku": "X", "price": "5.00", "stock_quantity": 1},
        headers=outsider_headers,
    )
    assert response.status_code == 404


def test_support_role_cannot_create_product(client):
    owner_headers = _register_and_login(client, "powner4@example.com")
    support_headers = _register_and_login(client, "psupport@example.com")
    store_id = _create_store(client, owner_headers, "permcheck")

    client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "psupport@example.com", "role": "support"},
        headers=owner_headers,
    )

    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Widget", "sku": "X", "price": "5.00", "stock_quantity": 1},
        headers=support_headers,
    )
    assert response.status_code == 403


def test_duplicate_sku_rejected(client):
    headers = _register_and_login(client, "powner5@example.com")
    store_id = _create_store(client, headers, "dupsku")
    _create_product(client, headers, store_id, sku="DUPE")

    response = _create_product(client, headers, store_id, sku="DUPE")
    assert response.status_code == 400


def test_update_and_delete_product(client):
    headers = _register_and_login(client, "powner6@example.com")
    store_id = _create_store(client, headers, "updatedelete")
    product_id = _create_product(client, headers, store_id).json()["id"]

    update_response = client.put(
        f"/api/v1/stores/{store_id}/products/{product_id}",
        json={"stock_quantity": 3},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["stock_quantity"] == 3

    delete_response = client.delete(
        f"/api/v1/stores/{store_id}/products/{product_id}", headers=headers
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/stores/{store_id}/products/{product_id}")
    assert get_response.status_code == 404
