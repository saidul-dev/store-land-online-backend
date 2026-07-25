from decimal import Decimal


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


def _create_variant(client, headers, store_id, sku="SKU-1", price="10.00", stock=100):
    response = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Widget", "variants": [{"sku": sku, "price": price, "stock_quantity": stock}]},
        headers=headers,
    )
    return response.json()["variants"][0]["id"]


def test_summary_requires_membership(client):
    owner_headers = _register_and_login(client, "aowner@example.com")
    outsider_headers = _register_and_login(client, "aoutsider@example.com")
    store_id = _create_store(client, owner_headers, "analyticsperm")

    response = client.get(f"/api/v1/stores/{store_id}/analytics/summary", headers=outsider_headers)
    assert response.status_code == 404


def test_summary_with_no_orders(client):
    headers = _register_and_login(client, "aowner2@example.com")
    store_id = _create_store(client, headers, "analyticsempty")

    response = client.get(f"/api/v1/stores/{store_id}/analytics/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_orders"] == 0
    assert Decimal(body["total_revenue"]) == Decimal("0")
    assert Decimal(body["average_order_value"]) == Decimal("0")
    assert body["daily"] == []


def test_summary_reflects_orders_and_excludes_cancelled_from_revenue(client):
    owner_headers = _register_and_login(client, "aowner3@example.com")
    customer_headers = _register_and_login(client, "acustomer3@example.com")
    store_id = _create_store(client, owner_headers, "analyticsdata")
    variant_id = _create_variant(client, owner_headers, store_id, price="10.00", stock=100)

    client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 2}]},
        headers=customer_headers,
    )
    cancelled_order = client.post(
        f"/api/v1/stores/{store_id}/orders/",
        json={"items": [{"variant_id": variant_id, "quantity": 1}]},
        headers=customer_headers,
    ).json()
    client.patch(
        f"/api/v1/stores/{store_id}/orders/{cancelled_order['id']}",
        json={"status": "cancelled"},
        headers=owner_headers,
    )

    response = client.get(f"/api/v1/stores/{store_id}/analytics/summary", headers=owner_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_orders"] == 2
    assert body["cancelled_orders"] == 1
    assert body["pending_orders"] == 1
    # only the non-cancelled order (qty 2 * 10.00) counts toward revenue
    assert Decimal(body["total_revenue"]) == Decimal("20.00")
    assert Decimal(body["average_order_value"]) == Decimal("20.00")
    assert body["total_products"] == 1
    assert body["total_customers"] == 1
    assert len(body["daily"]) == 1
    assert body["daily"][0]["orders"] == 2


def test_summary_days_filter_rejects_out_of_range(client):
    headers = _register_and_login(client, "aowner4@example.com")
    store_id = _create_store(client, headers, "analyticsrange")

    response = client.get(f"/api/v1/stores/{store_id}/analytics/summary?days=0", headers=headers)
    assert response.status_code == 422
