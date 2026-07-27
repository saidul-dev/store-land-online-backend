from app.models.plan import Plan
from app.models.user import User


def _register_and_login(client, email, password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_super_admin(db_session, email):
    user = db_session.query(User).filter(User.email == email).first()
    user.is_super_admin = True
    db_session.commit()


def _create_store(client, headers, subdomain):
    return client.post(
        "/api/v1/stores/", json={"name": "Test Store", "subdomain": subdomain}, headers=headers
    ).json()["id"]


def test_non_super_admin_cannot_access_admin_routes(client):
    headers = _register_and_login(client, "regular@example.com")
    response = client.get("/api/v1/admin/stores", headers=headers)
    assert response.status_code == 403


def test_super_admin_can_list_stores_with_subscription(client, db_session):
    admin_headers = _register_and_login(client, "admin@example.com")
    _make_super_admin(db_session, "admin@example.com")

    owner_headers = _register_and_login(client, "merchant@example.com")
    _create_store(client, owner_headers, "merchantstore")

    response = client.get("/api/v1/admin/stores", headers=admin_headers)
    assert response.status_code == 200
    stores = response.json()
    merchant_store = next(s for s in stores if s["subdomain"] == "merchantstore")
    assert merchant_store["owner_email"] == "merchant@example.com"
    assert merchant_store["subscription"]["plan"]["slug"] == "free"


def test_super_admin_can_list_plans(client, db_session):
    admin_headers = _register_and_login(client, "admin2@example.com")
    _make_super_admin(db_session, "admin2@example.com")

    response = client.get("/api/v1/admin/plans", headers=admin_headers)
    assert response.status_code == 200
    slugs = {p["slug"] for p in response.json()}
    assert slugs == {"free", "basic", "pro"}


def test_super_admin_can_change_store_plan(client, db_session):
    admin_headers = _register_and_login(client, "admin3@example.com")
    _make_super_admin(db_session, "admin3@example.com")

    owner_headers = _register_and_login(client, "merchant2@example.com")
    store_id = _create_store(client, owner_headers, "upgrademe")

    pro_plan = db_session.query(Plan).filter(Plan.slug == "pro").first()
    response = client.patch(
        f"/api/v1/admin/stores/{store_id}/subscription",
        json={"plan_id": pro_plan.id, "status": "active", "current_period_end": None},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["plan"]["slug"] == "pro"
    assert response.json()["status"] == "active"

    # The store's own subscription view should reflect the change immediately.
    sub_response = client.get(f"/api/v1/stores/{store_id}/subscription", headers=owner_headers)
    assert sub_response.json()["subscription"]["plan"]["slug"] == "pro"


def test_change_plan_rejects_unknown_plan_id(client, db_session):
    admin_headers = _register_and_login(client, "admin4@example.com")
    _make_super_admin(db_session, "admin4@example.com")

    owner_headers = _register_and_login(client, "merchant3@example.com")
    store_id = _create_store(client, owner_headers, "badplan")

    response = client.patch(
        f"/api/v1/admin/stores/{store_id}/subscription",
        json={"plan_id": 999999},
        headers=admin_headers,
    )
    assert response.status_code == 404
