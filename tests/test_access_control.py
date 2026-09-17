from datetime import datetime, timedelta, timezone

import jwt


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
    forged = jwt.encode(payload, "attacker-secret", algorithm="HS256")
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
