import os

MIN_SECRET_BYTES = 32


class ConfigError(RuntimeError):
    pass


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    JWT_SECRET = os.environ.get("JWT_SECRET", "")
    JWT_ALGORITHM = "HS256"
    JWT_TTL_SECONDS = int(os.environ.get("JWT_TTL_SECONDS", "3600"))
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    BCRYPT_ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))
    MAX_USERNAME_LENGTH = 64
    MAX_PASSWORD_LENGTH = 128
    MAX_TITLE_LENGTH = 200
    MAX_BODY_LENGTH = 5000


def validate(config: dict) -> None:
    for key in ("SECRET_KEY", "JWT_SECRET"):
        value = config.get(key) or ""
        if len(value.encode("utf-8")) < MIN_SECRET_BYTES:
            raise ConfigError(
                f"{key} must be set to at least {MIN_SECRET_BYTES} bytes; "
                "generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
