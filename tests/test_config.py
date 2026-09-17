import pytest

from app import create_app
from app.config import ConfigError

STRONG = "a" * 32


def test_weak_jwt_secret_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        create_app({"DATABASE_URL": f"sqlite:///{tmp_path / 'x.db'}", "SECRET_KEY": STRONG, "JWT_SECRET": "short"})


def test_missing_secret_key_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        create_app({"DATABASE_URL": f"sqlite:///{tmp_path / 'x.db'}", "SECRET_KEY": "", "JWT_SECRET": STRONG})
