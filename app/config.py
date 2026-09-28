import os

MIN_SECRET_BYTES = 32


class ConfigError(RuntimeError):
    pass


class Config:
    JWT_SECRET = os.environ.get("JWT_SECRET", "")
    JWT_ALGORITHM = "HS256"
    JWT_TTL_SECONDS = int(os.environ.get("JWT_TTL_SECONDS", "3600"))
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    BCRYPT_ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))


def validate(config: dict) -> None:
    secret = config["JWT_SECRET"]
    if len(secret.encode("utf-8")) < MIN_SECRET_BYTES:
        raise ConfigError(
            f"JWT_SECRET must be set to at least {MIN_SECRET_BYTES} bytes; "
            "generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )
