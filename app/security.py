from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from app.models import User

AUTH_SCHEME = "Bearer"


def issue_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=current_app.config["JWT_TTL_SECONDS"])).timestamp()),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=current_app.config["JWT_ALGORITHM"])


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=[current_app.config["JWT_ALGORITHM"]],
        options={"require": ["exp", "iat", "sub"]},
    )


def _unauthorized(message: str):
    return jsonify({"error": message}), 401


def jwt_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != AUTH_SCHEME.lower() or not token.strip():
            return _unauthorized("authorization header missing or malformed")

        try:
            payload = decode_token(token.strip())
        except jwt.ExpiredSignatureError:
            return _unauthorized("token expired")
        except jwt.InvalidTokenError:
            return _unauthorized("invalid token")

        session = current_app.session_factory()
        try:
            user = session.get(User, int(payload["sub"]))
            if user is None:
                return _unauthorized("invalid token")
            g.current_user_id = user.id
            g.current_username = user.username
            g.current_role = user.role
        finally:
            session.close()

        return view(*args, **kwargs)

    return wrapper
