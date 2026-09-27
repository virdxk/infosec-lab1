from datetime import datetime, timedelta, timezone

import jwt
import pytest


def test_data_requires_token(client):
    response = client.get("/api/data")
    assert response.status_code == 401


def test_data_with_valid_token(client, auth_headers):
    response = client.get("/api/data", headers=auth_headers)
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 1
    assert body["items"][0]["title"] == "Seeded"


def test_malformed_authorization_header_is_rejected(client, token):
    for header in ["", "Bearer", "Bearer ", token, f"Basic {token}"]:
        response = client.get("/api/data", headers={"Authorization": header})
        assert response.status_code == 401, header


def test_token_signed_with_another_key_is_rejected(client, app):
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    forged = jwt.encode(payload, "attacker-secret-that-is-at-least-32-bytes", algorithm="HS256")
    response = client.get("/api/data", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


def test_unsigned_alg_none_token_is_rejected(client):
    payload = {
        "sub": "1",
        "role": "admin",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    forged = jwt.encode(payload, key="", algorithm="none")
    response = client.get("/api/data", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


def test_expired_token_is_rejected(client, app):
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(past.timestamp()),
        "exp": int((past + timedelta(hours=1)).timestamp()),
    }
    expired = jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")
    response = client.get("/api/data", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "token expired"


def test_create_post_requires_token(client):
    response = client.post("/api/posts", json={"title": "t", "body": "b"})
    assert response.status_code == 401


@pytest.mark.parametrize("subject", ["not-an-id", "9" * 100, "999", 1, 1.5])
@pytest.mark.parametrize("method, path", [("GET", "/api/data"), ("POST", "/api/posts")])
def test_invalid_subject_is_rejected_before_api_handler(client, app, subject, method, path):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(hours=1)).timestamp())},
        app.config["JWT_SECRET"],
        algorithm="HS256",
    )

    response = client.open(path, method=method, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid token"}


def test_health_stays_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_authentication_runs_before_post_validation(client):
    response = client.post("/api/posts", data='[1]', content_type="application/json")
    assert response.status_code == 401


@pytest.mark.parametrize("path, allowed_method", [("/api/data", "GET"), ("/api/posts", "POST")])
def test_automatic_options_stays_public(client, path, allowed_method):
    response = client.options(path)
    assert response.status_code == 200
    assert allowed_method in response.headers["Allow"]
