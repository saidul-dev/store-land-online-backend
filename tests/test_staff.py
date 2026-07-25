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


def test_owner_is_auto_added_as_member(client):
    owner_headers = _register_and_login(client, "owner@example.com")
    store_id = _create_store(client, owner_headers, "ownerstore")

    response = client.get(f"/api/v1/stores/{store_id}/staff/", headers=owner_headers)
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 1
    assert members[0]["role"] == "owner"
    assert members[0]["user_email"] == "owner@example.com"


def test_owner_can_add_staff(client):
    owner_headers = _register_and_login(client, "owner2@example.com")
    _register_and_login(client, "staffer@example.com")
    store_id = _create_store(client, owner_headers, "addstaff")

    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "staffer@example.com", "role": "staff"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["role"] == "staff"


def test_add_staff_unregistered_email_fails(client):
    owner_headers = _register_and_login(client, "owner3@example.com")
    store_id = _create_store(client, owner_headers, "noemail")

    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "ghost@example.com", "role": "staff"},
        headers=owner_headers,
    )
    assert response.status_code == 404


def test_add_duplicate_member_fails(client):
    owner_headers = _register_and_login(client, "owner4@example.com")
    _register_and_login(client, "dupe@example.com")
    store_id = _create_store(client, owner_headers, "dupestore")

    client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "dupe@example.com", "role": "staff"},
        headers=owner_headers,
    )
    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "dupe@example.com", "role": "manager"},
        headers=owner_headers,
    )
    assert response.status_code == 400


def test_cannot_assign_owner_role_via_api(client):
    owner_headers = _register_and_login(client, "owner5@example.com")
    store_id = _create_store(client, owner_headers, "noownerassign")

    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "owner5@example.com", "role": "owner"},
        headers=owner_headers,
    )
    assert response.status_code == 422


def test_non_member_cannot_view_staff(client):
    owner_headers = _register_and_login(client, "owner6@example.com")
    outsider_headers = _register_and_login(client, "outsider@example.com")
    store_id = _create_store(client, owner_headers, "privatestore")

    response = client.get(f"/api/v1/stores/{store_id}/staff/", headers=outsider_headers)
    assert response.status_code == 404


def test_staff_role_cannot_manage_staff(client):
    owner_headers = _register_and_login(client, "owner7@example.com")
    staff_headers = _register_and_login(client, "limited@example.com")
    store_id = _create_store(client, owner_headers, "limitedperms")

    client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "limited@example.com", "role": "staff"},
        headers=owner_headers,
    )

    # "staff" role has products/orders permissions but not staff.manage
    response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "owner7@example.com", "role": "support"},
        headers=staff_headers,
    )
    assert response.status_code == 403


def test_owner_can_update_and_remove_staff_role(client):
    owner_headers = _register_and_login(client, "owner8@example.com")
    _register_and_login(client, "rolechange@example.com")
    store_id = _create_store(client, owner_headers, "rolechangestore")

    add_response = client.post(
        f"/api/v1/stores/{store_id}/staff/",
        json={"email": "rolechange@example.com", "role": "staff"},
        headers=owner_headers,
    )
    membership_id = add_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/stores/{store_id}/staff/{membership_id}",
        json={"role": "manager"},
        headers=owner_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "manager"

    delete_response = client.delete(
        f"/api/v1/stores/{store_id}/staff/{membership_id}", headers=owner_headers
    )
    assert delete_response.status_code == 204

    list_response = client.get(f"/api/v1/stores/{store_id}/staff/", headers=owner_headers)
    assert len(list_response.json()) == 1


def test_cannot_change_or_remove_owner(client):
    owner_headers = _register_and_login(client, "owner9@example.com")
    store_id = _create_store(client, owner_headers, "protectowner")

    staff_list = client.get(f"/api/v1/stores/{store_id}/staff/", headers=owner_headers).json()
    owner_membership_id = staff_list[0]["id"]

    update_response = client.patch(
        f"/api/v1/stores/{store_id}/staff/{owner_membership_id}",
        json={"role": "staff"},
        headers=owner_headers,
    )
    assert update_response.status_code == 400

    delete_response = client.delete(
        f"/api/v1/stores/{store_id}/staff/{owner_membership_id}", headers=owner_headers
    )
    assert delete_response.status_code == 400
