from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

from app.models import User
from app.security import issue_token

bp = Blueprint("auth", __name__, url_prefix="/auth")

INVALID_CREDENTIALS = {"error": "invalid credentials"}
AUTH_SCHEME = "Bearer"


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    if len(username) > current_app.config["MAX_USERNAME_LENGTH"]:
        return jsonify({"error": "username is too long"}), 400
    if len(password) > current_app.config["MAX_PASSWORD_LENGTH"]:
        return jsonify({"error": "password is too long"}), 400

    session = current_app.session_factory()
    try:
        user = session.scalar(select(User).where(User.username == username))
        if user is None or not user.check_password(password):
            return jsonify(INVALID_CREDENTIALS), 401
        token = issue_token(user)
    finally:
        session.close()

    return (
        jsonify(
            {
                "access_token": token,
                "token_type": AUTH_SCHEME,
                "expires_in": current_app.config["JWT_TTL_SECONDS"],
            }
        ),
        200,
    )
