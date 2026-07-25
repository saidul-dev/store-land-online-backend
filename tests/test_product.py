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


def _create_product(client, headers, store_id, sku="SKU-1", price="19.99", stock=10, **extra):
    payload = {
        "name": "Widget",
        "variants": [{"sku": sku, "price": price, "stock_quantity": stock}],
    }
    payload.update(extra)
    return client.post(f"/api/v1/stores/{store_id}/products/", json=payload, headers=headers)


def test_owner_can_create_product_with_variant(client):
    headers = _register_and_login(client, "powner@example.com")
    store_id = _create_store(client, headers, "productstore")

    response = _create_product(client, headers, store_id)
    assert response.status_code == 201
    body = response.json()
    assert len(body["variants"]) == 1
    assert body["variants"][0]["sku"] == "SKU-1"
    assert body["variants"][0]["stock_quantity"] == 10


def test_product_can_have_multiple_variants(client):
    headers = _register_and_login(client, "pmulti@example.com")
    store_id = _create_store(client, headers, "multivariant")

    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={
            "name": "T-Shirt",
            "variants": [
                {"sku": "TS-RED-M", "price": "15.00", "stock_quantity": 5, "attributes": {"color": "red", "size": "M"}},
                {"sku": "TS-BLUE-L", "price": "15.00", "stock_quantity": 3, "attributes": {"color": "blue", "size": "L"}},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert len(response.json()["variants"]) == 2


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
        json={"name": "Widget", "variants": [{"sku": "X", "price": "5.00", "stock_quantity": 1}]},
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
        json={"name": "Widget", "variants": [{"sku": "X", "price": "5.00", "stock_quantity": 1}]},
        headers=support_headers,
    )
    assert response.status_code == 403


def test_duplicate_sku_rejected(client):
    headers = _register_and_login(client, "powner5@example.com")
    store_id = _create_store(client, headers, "dupsku")
    _create_product(client, headers, store_id, sku="DUPE")

    response = _create_product(client, headers, store_id, sku="DUPE")
    assert response.status_code == 400


def test_duplicate_sku_within_same_payload_rejected(client):
    headers = _register_and_login(client, "powner5b@example.com")
    store_id = _create_store(client, headers, "dupskusame")

    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={
            "name": "Widget",
            "variants": [
                {"sku": "SAME", "price": "5.00", "stock_quantity": 1},
                {"sku": "SAME", "price": "6.00", "stock_quantity": 1},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 400


def test_update_product_and_manage_variants(client):
    headers = _register_and_login(client, "powner6@example.com")
    store_id = _create_store(client, headers, "updatedelete")
    product_id = _create_product(client, headers, store_id).json()["id"]

    update_response = client.put(
        f"/api/v1/stores/{store_id}/products/{product_id}",
        json={"name": "Renamed Widget"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Renamed Widget"

    variant_response = client.post(
        f"/api/v1/stores/{store_id}/products/{product_id}/variants",
        json={"sku": "SKU-2", "price": "25.00", "stock_quantity": 4},
        headers=headers,
    )
    assert variant_response.status_code == 201
    variant_id = variant_response.json()["id"]

    variant_update = client.put(
        f"/api/v1/stores/{store_id}/products/{product_id}/variants/{variant_id}",
        json={"stock_quantity": 1},
        headers=headers,
    )
    assert variant_update.status_code == 200
    assert variant_update.json()["stock_quantity"] == 1

    variant_delete = client.delete(
        f"/api/v1/stores/{store_id}/products/{product_id}/variants/{variant_id}", headers=headers
    )
    assert variant_delete.status_code == 204

    delete_response = client.delete(
        f"/api/v1/stores/{store_id}/products/{product_id}", headers=headers
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/stores/{store_id}/products/{product_id}")
    assert get_response.status_code == 404


def test_product_with_category_and_brand(client):
    headers = _register_and_login(client, "powner7@example.com")
    store_id = _create_store(client, headers, "catbrand")

    category_id = client.post(
        f"/api/v1/stores/{store_id}/categories/",
        json={"name": "Electronics", "slug": "electronics"},
        headers=headers,
    ).json()["id"]
    brand_id = client.post(
        f"/api/v1/stores/{store_id}/brands/",
        json={"name": "Acme", "slug": "acme"},
        headers=headers,
    ).json()["id"]

    response = _create_product(client, headers, store_id, category_id=category_id, brand_id=brand_id)
    assert response.status_code == 201
    body = response.json()
    assert body["category_id"] == category_id
    assert body["brand_id"] == brand_id

    filtered = client.get(f"/api/v1/stores/{store_id}/products/?category_id={category_id}")
    assert len(filtered.json()) == 1
