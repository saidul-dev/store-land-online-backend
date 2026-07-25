def _auth_headers(client, email="post@example.com", password="testpass123"):
    client.post("/api/v1/register", json={"email": email, "password": password})
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_post_requires_auth(client):
    response = client.post("/api/v1/posts/", json={"title": "Hello", "content": "World"})
    assert response.status_code == 401


def test_create_and_list_posts(client):
    headers = _auth_headers(client)
    response = client.post("/api/v1/posts/", json={"title": "Hello", "content": "World"}, headers=headers)
    assert response.status_code == 201
    post_id = response.json()["id"]

    response = client.get("/api/v1/posts/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Hello"


def test_cannot_edit_others_post(client):
    headers_a = _auth_headers(client, email="a@example.com")
    response = client.post("/api/v1/posts/", json={"title": "A's post", "content": "..."}, headers=headers_a)
    post_id = response.json()["id"]

    headers_b = _auth_headers(client, email="b@example.com")
    response = client.put(
        f"/api/v1/posts/{post_id}", json={"title": "hacked", "content": "..."}, headers=headers_b
    )
    assert response.status_code == 403
