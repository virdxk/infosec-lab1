import pytest

from app import create_app
from app.models import Post, User

USERNAME = "alice"
PASSWORD = "Al1ce-Str0ng-Pass!"
SECRET = "test-secret-value-long-enough-for-hs256"


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {"DATABASE_URL": f"sqlite:///{tmp_path / 'test.db'}", "JWT_SECRET": SECRET, "BCRYPT_ROUNDS": 4}
    )
    with app.session_factory() as session:
        user = User(username=USERNAME)
        user.set_password(PASSWORD, 4)
        session.add(user)
        session.flush()
        session.add(Post(author_id=user.id, title="Seeded", body="Seeded body"))
        session.commit()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={"username": USERNAME, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.get_json()['access_token']}"}
