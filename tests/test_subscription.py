from app.models.plan import Plan
from app.models.subscription import Subscription


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


def test_new_store_gets_free_trial(client):
    headers = _register_and_login(client, "trialowner@example.com")
    store_id = _create_store(client, headers, "trialstore")

    response = client.get(f"/api/v1/stores/{store_id}/subscription", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["subscription"]["status"] == "trialing"
    assert body["subscription"]["plan"]["slug"] == "free"
    assert body["subscription"]["current_period_end"] is not None
    assert body["is_expired"] is False
    assert body["products_used"] == 0
    assert body["staff_used"] == 1


def test_product_limit_enforced_for_plan(client, db_session):
    headers = _register_and_login(client, "limitowner@example.com")
    store_id = _create_store(client, headers, "limitstore")

    tiny_plan = Plan(name="Tiny", slug="tiny-test", price=0, billing_cycle="trial", max_products=1, max_staff=1)
    db_session.add(tiny_plan)
    db_session.commit()
    sub = db_session.query(Subscription).filter(Subscription.store_id == store_id).first()
    sub.plan_id = tiny_plan.id
    db_session.commit()

    first = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "One", "variants": [{"sku": "LIMIT-1", "price": "5.00", "stock_quantity": 1}]},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/v1/stores/{store_id}/products/",
        json={"name": "Two", "variants": [{"sku": "LIMIT-2", "price": "5.00", "stock_quantity": 1}]},
        headers=headers,
    )
    assert second.status_code == 400
    assert "limit" in second.json()["detail"].lower()


def test_subscription_status_readable_by_any_role(client, db_session):
    # Unlike GET .../subscription (BILLING_VIEW only), the /status endpoint is
    # just "is this store locked" — every role needs it to explain blocked edits.
    owner_headers = _register_and_login(client, "statusowner@example.com")
    staff_headers = _register_and_login(client, "statusstaff@example.com")
    store_id = _create_store(client, owner_headers, "statusstore")
    client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "statusstaff@example.com", "role": "support"},
        headers=owner_headers,
    )

    response = client.get(f"/api/v1/stores/{store_id}/subscription/status", headers=staff_headers)
    assert response.status_code == 200
    assert response.json() == {"is_expired": False}

    sub = db_session.query(Subscription).filter(Subscription.store_id == store_id).first()
    sub.status = "expired"
    db_session.commit()

    response = client.get(f"/api/v1/stores/{store_id}/subscription/status", headers=staff_headers)
    assert response.json() == {"is_expired": True}


def test_expired_subscription_blocks_edits_but_allows_reads(client, db_session):
    headers = _register_and_login(client, "expiredowner@example.com")
    store_id = _create_store(client, headers, "expiredstore")

    sub = db_session.query(Subscription).filter(Subscription.store_id == store_id).first()
    sub.status = "expired"
    db_session.commit()

    create_response = client.post(
        f"/api/v1/stores/{store_id}/brands/", json={"name": "Acme", "slug": "acme"}, headers=headers
    )
    assert create_response.status_code == 402

    read_response = client.get(f"/api/v1/stores/{store_id}/brands/", headers=headers)
    assert read_response.status_code == 200


def test_staff_limit_enforced_for_plan(client, db_session):
    owner_headers = _register_and_login(client, "staffcapowner@example.com")
    _register_and_login(client, "staffcapinvitee@example.com")
    store_id = _create_store(client, owner_headers, "staffcapstore")

    sub = db_session.query(Subscription).filter(Subscription.store_id == store_id).first()
    sub.plan.max_staff = 1  # owner alone already fills a 1-seat plan
    db_session.commit()

    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "staffcapinvitee@example.com", "role": "staff"},
        headers=owner_headers,
    )
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()
