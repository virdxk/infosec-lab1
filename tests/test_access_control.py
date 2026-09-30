from datetime import datetime, timedelta, timezone

import jwt


def make_token(secret, algorithm="HS256", expires_in=timedelta(hours=1)):
    now = datetime.now(timezone.utc)
    payload = {"sub": "1", "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, secret, algorithm=algorithm)


def get_data(client, token):
    return client.get("/api/data", headers={"Authorization": f"Bearer {token}"})


def test_no_token(client):
    assert client.get("/api/data").status_code == 401
    assert client.post("/api/posts", json={"title": "t", "body": "b"}).status_code == 401


def test_valid_token(client, auth_headers):
    response = client.get("/api/data", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()[0]["title"] == "Seeded"


def test_forged_signature(client):
    token = make_token("attacker-secret-that-is-at-least-32-bytes")
    assert get_data(client, token).status_code == 401


def test_alg_none(client):
    token = make_token(None, algorithm="none")
    assert get_data(client, token).status_code == 401


def test_expired(client, app):
    token = make_token(app.config["JWT_SECRET"], expires_in=timedelta(hours=-1))
    assert get_data(client, token).status_code == 401
