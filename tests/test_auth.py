from tests.conftest import TEST_PASSWORD, TEST_USERNAME


def test_login_returns_token(client):
    response = client.post("/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    body = response.get_json()
    assert body["token_type"] == "Bearer"
    assert body["access_token"].count(".") == 2


def test_login_with_wrong_password_is_rejected(client):
    response = client.post("/auth/login", json={"username": TEST_USERNAME, "password": "wrong-password"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid credentials"}


def test_unknown_user_and_wrong_password_are_indistinguishable(client):
    unknown = client.post("/auth/login", json={"username": "nobody", "password": "whatever"})
    wrong = client.post("/auth/login", json={"username": TEST_USERNAME, "password": "wrong-password"})
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.get_json() == wrong.get_json()


def test_login_without_body_is_rejected(client):
    response = client.post("/auth/login", json={})
    assert response.status_code == 400


def test_login_with_oversized_username_is_rejected(client):
    response = client.post("/auth/login", json={"username": "a" * 500, "password": TEST_PASSWORD})
    assert response.status_code == 400


def test_sql_injection_in_username_does_not_grant_access(client):
    payloads = ["' OR '1'='1' -- ", "admin'--", "' OR 1=1;--", "\" OR \"\"=\""]
    for payload in payloads:
        response = client.post("/auth/login", json={"username": payload, "password": "anything"})
        assert response.status_code == 401, payload


def test_password_is_stored_as_bcrypt_hash(app):
    from sqlalchemy import select

    from app.models import User

    session = app.session_factory()
    try:
        user = session.scalar(select(User).where(User.username == TEST_USERNAME))
        assert user.password_hash != TEST_PASSWORD
        assert user.password_hash.startswith("$2b$")
        assert len(user.password_hash) == 60
    finally:
        session.close()
