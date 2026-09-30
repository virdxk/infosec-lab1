def test_create(client, auth_headers):
    response = client.post("/api/posts", json={"title": "Hello", "body": "World"}, headers=auth_headers)
    assert response.status_code == 201
    assert response.get_json()["author"] == "alice"


def test_missing_fields(client, auth_headers):
    response = client.post("/api/posts", json={"title": "only title"}, headers=auth_headers)
    assert response.status_code == 400


def test_xss_is_escaped(client, auth_headers):
    payload = "<script>alert(1)</script>"
    created = client.post("/api/posts", json={"title": "x", "body": payload}, headers=auth_headers)
    assert created.get_json()["body"] == "&lt;script&gt;alert(1)&lt;/script&gt;"

    listed = client.get("/api/data", headers=auth_headers)
    assert "<script>" not in listed.get_data(as_text=True)
