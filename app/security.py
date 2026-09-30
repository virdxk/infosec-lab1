from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

ALGORITHM = "HS256"


def issue_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=current_app.config["JWT_TTL_SECONDS"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=[ALGORITHM],
        options={"require": ["sub", "iat", "exp"]},
    )
