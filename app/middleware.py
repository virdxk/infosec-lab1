import jwt
from flask import current_app, g, jsonify, request

from app.models import User
from app.security import AUTH_SCHEME, decode_token


def authenticate_request():
    if request.method == "OPTIONS":
        return None

    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != AUTH_SCHEME.lower() or not token.strip():
        return jsonify({"error": "authorization header missing or malformed"}), 401

    try:
        claims = decode_token(token.strip())
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid token"}), 401

    with current_app.session_factory() as session:
        try:
            user = session.get(User, int(claims["sub"]))
        except (ValueError, OverflowError):
            return jsonify({"error": "invalid token"}), 401

        if user is None:
            return jsonify({"error": "invalid token"}), 401

        g.current_user_id = user.id
        g.current_username = user.username
        g.current_role = user.role

    return None
