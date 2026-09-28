import pytest

from app import create_app
from app.config import ConfigError


def test_weak_jwt_secret_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        create_app(
            {
                "DATABASE_URL": f"sqlite:///{tmp_path / 'x.db'}",
                "JWT_SECRET": "short",
            }
        )


def test_missing_jwt_secret_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        create_app(
            {
                "DATABASE_URL": f"sqlite:///{tmp_path / 'x.db'}",
                "JWT_SECRET": "",
            }
        )
