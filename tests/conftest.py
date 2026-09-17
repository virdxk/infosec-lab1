import pytest

from app import create_app
from app.models import Post, User

TEST_USERNAME = "alice"
TEST_PASSWORD = "Al1ce-Str0ng-Pass!"
TEST_SECRET = "test-secret-value-long-enough-for-hs256-abcdef"


@pytest.fixture
def app(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": database_url,
            "SECRET_KEY": TEST_SECRET,
            "JWT_SECRET": TEST_SECRET,
            "BCRYPT_ROUNDS": 4,
        }
    )

    session = application.session_factory()
    try:
        user = User(username=TEST_USERNAME, role="user")
        user.set_password(TEST_PASSWORD, application.config["BCRYPT_ROUNDS"])
        session.add(user)
        session.commit()
        session.add(Post(author_id=user.id, title="Seeded", body="Seeded body"))
        session.commit()
    finally:
        session.close()

    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def token(client):
    response = client.post("/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    return response.get_json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
