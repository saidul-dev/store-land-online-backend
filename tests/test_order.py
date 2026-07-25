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


def _create_variant(client, headers, store_id, sku="SKU-1", price="10.00", stock=5):
    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Widget", "variants": [{"sku": sku, "price": price, "stock_quantity": stock}]},
        headers=headers,
    )
    return response.json()["variants"][0]["id"]


def test_checkout_creates_order_and_decrements_stock(client):
    owner_headers = _register_and_login(client, "oowner@example.com")
    customer_headers = _register_and_login(client, "ocustomer@example.com")
    store_id = _create_store(client, owner_headers, "checkoutstore")
    variant_id = _create_variant(client, owner_headers, store_id, stock=5)

    response = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 2}]},
        headers=customer_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["total_amount"] == "20.00"
    assert body["status"] == "pending"

    product_id = client.get(f"/api/v1/stores/{store_id}/products/").json()[0]["id"]
    product = client.get(f"/api/v1/stores/{store_id}/products/{product_id}").json()
    assert product["variants"][0]["stock_quantity"] == 3


def test_checkout_insufficient_stock_fails(client):
    owner_headers = _register_and_login(client, "oowner2@example.com")
    customer_headers = _register_and_login(client, "ocustomer2@example.com")
    store_id = _create_store(client, owner_headers, "lowstock")
    variant_id = _create_variant(client, owner_headers, store_id, stock=1)

    response = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 5}]},
        headers=customer_headers,
    )
    assert response.status_code == 400


def test_checkout_unknown_variant_fails(client):
    owner_headers = _register_and_login(client, "oowner3@example.com")
    customer_headers = _register_and_login(client, "ocustomer3@example.com")
    store_id = _create_store(client, owner_headers, "unknownvariant")

    response = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": 999999, "quantity": 1}]},
        headers=customer_headers,
    )
    assert response.status_code == 404


def test_list_my_orders(client):
    owner_headers = _register_and_login(client, "oowner4@example.com")
    customer_headers = _register_and_login(client, "ocustomer4@example.com")
    store_id = _create_store(client, owner_headers, "mineorders")
    variant_id = _create_variant(client, owner_headers, store_id)

    client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    )

    response = client.get(f"/api/v1/stores/{store_id}/orders/mine", headers=customer_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_non_member_cannot_list_all_orders(client):
    owner_headers = _register_and_login(client, "oowner5@example.com")
    customer_headers = _register_and_login(client, "ocustomer5@example.com")
    store_id = _create_store(client, owner_headers, "staffonly")

    response = client.get(f"/api/v1/stores/{store_id}/orders/", headers=customer_headers)
    assert response.status_code == 404


def test_owner_can_view_any_order_and_customer_can_view_own(client):
    owner_headers = _register_and_login(client, "oowner6@example.com")
    customer_headers = _register_and_login(client, "ocustomer6@example.com")
    store_id = _create_store(client, owner_headers, "vieworder")
    variant_id = _create_variant(client, owner_headers, store_id)

    order_id = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    ).json()["id"]

    owner_view = client.get(f"/api/v1/stores/{store_id}/orders/{order_id}", headers=owner_headers)
    assert owner_view.status_code == 200

    customer_view = client.get(
        f"/api/v1/stores/{store_id}/orders/{order_id}", headers=customer_headers
    )
    assert customer_view.status_code == 200


def test_other_customer_cannot_view_order(client):
    owner_headers = _register_and_login(client, "oowner7@example.com")
    customer_headers = _register_and_login(client, "ocustomer7@example.com")
    other_customer_headers = _register_and_login(client, "ocustomer7b@example.com")
    store_id = _create_store(client, owner_headers, "otherorder")
    variant_id = _create_variant(client, owner_headers, store_id)

    order_id = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    ).json()["id"]

    response = client.get(
        f"/api/v1/stores/{store_id}/orders/{order_id}", headers=other_customer_headers
    )
    assert response.status_code == 403


def test_staff_can_update_order_status(client):
    owner_headers = _register_and_login(client, "oowner8@example.com")
    customer_headers = _register_and_login(client, "ocustomer8@example.com")
    store_id = _create_store(client, owner_headers, "statusupdate")
    variant_id = _create_variant(client, owner_headers, store_id)

    order_id = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    ).json()["id"]

    response = client.patch(
        f"/api/v1/stores/{store_id}/orders/{order_id}",
        json={"status": "shipped"},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


def test_invalid_status_rejected(client):
    owner_headers = _register_and_login(client, "oowner9@example.com")
    customer_headers = _register_and_login(client, "ocustomer9@example.com")
    store_id = _create_store(client, owner_headers, "invalidstatus")
    variant_id = _create_variant(client, owner_headers, store_id)

    order_id = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    ).json()["id"]

    response = client.patch(
        f"/api/v1/stores/{store_id}/orders/{order_id}",
        json={"status": "teleported"},
        headers=owner_headers,
    )
    assert response.status_code == 422
