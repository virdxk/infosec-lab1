import pytest


def test_create_post(client, auth_headers):
    response = client.post("/api/posts", json={"title": "Hello", "body": "World"}, headers=auth_headers)
    assert response.status_code == 201
    body = response.get_json()
    assert body["title"] == "Hello"
    assert body["author"] == "alice"


def test_create_post_validates_input(client, auth_headers):
    for payload in [{}, {"title": "only title"}, {"title": "", "body": ""}, {"title": 1, "body": 2}]:
        response = client.post("/api/posts", json=payload, headers=auth_headers)
        assert response.status_code == 400, payload


@pytest.mark.parametrize("body", ['[1]', '"text"', '7', 'true', 'null', '{'])
def test_create_post_rejects_invalid_json_body(client, auth_headers, body):
    response = client.post("/api/posts", data=body, content_type="application/json", headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": "title and body are required"}


def test_post_has_no_custom_length_limits(client, auth_headers):
    response = client.post("/api/posts", json={"title": "t" * 300, "body": "x" * 6000}, headers=auth_headers)
    assert response.status_code == 201
    assert response.get_json()["title"] == "t" * 300
    assert response.get_json()["body"] == "x" * 6000


def test_xss_payload_is_escaped_in_response(client, auth_headers):
    payload = "<script>alert('xss')</script>"
    created = client.post("/api/posts", json={"title": payload, "body": payload}, headers=auth_headers)
    assert created.status_code == 201
    assert "<script>" not in created.get_data(as_text=True)
    assert created.get_json()["title"] == "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;"

    listed = client.get("/api/data", headers=auth_headers)
    assert "<script>" not in listed.get_data(as_text=True)


def test_image_onerror_payload_is_escaped(client, auth_headers):
    payload = '<img src=x onerror="alert(1)">'
    client.post("/api/posts", json={"title": "img", "body": payload}, headers=auth_headers)
    listed = client.get("/api/data", headers=auth_headers)
    assert "onerror=\"alert(1)\"" not in listed.get_data(as_text=True)
    assert "&lt;img" in listed.get_data(as_text=True)
