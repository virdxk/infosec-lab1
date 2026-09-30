import os


class Config:
    JWT_SECRET = os.environ.get("JWT_SECRET", "")
    JWT_TTL_SECONDS = 3600
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    BCRYPT_ROUNDS = 12
