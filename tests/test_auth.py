import pytest
from sqlalchemy import select

from app.models import User
from tests.conftest import PASSWORD, USERNAME


def login(client, username, password):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_login_ok(client):
    response = login(client, USERNAME, PASSWORD)
    assert response.status_code == 200
    assert response.get_json()["access_token"].count(".") == 2


@pytest.mark.parametrize("username, password", [(USERNAME, "wrong"), ("nobody", PASSWORD)])
def test_bad_credentials(client, username, password):
    response = login(client, username, password)
    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid credentials"}


def test_empty_body(client):
    assert client.post("/auth/login", json={}).status_code == 400


def test_sqli(client):
    for payload in ["' OR '1'='1' --", "alice'--"]:
        assert login(client, payload, "anything").status_code == 401


def test_password_is_hashed(app):
    with app.session_factory() as session:
        user = session.scalar(select(User).where(User.username == USERNAME))
    assert user.password_hash.startswith("$2b$")
    assert PASSWORD not in user.password_hash
