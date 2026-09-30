import jwt
from flask import current_app, g, jsonify, request

from app.models import User
from app.security import decode_token


def authenticate_request():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return jsonify({"error": "missing token"}), 401

    try:
        claims = decode_token(header.removeprefix("Bearer "))
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid token"}), 401

    with current_app.session_factory() as session:
        user = session.get(User, int(claims["sub"]))
    if user is None:
        return jsonify({"error": "invalid token"}), 401

    g.user_id = user.id
    return None
