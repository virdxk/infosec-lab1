from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

from app.models import User
from app.security import issue_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "username and password are required"}), 400

    with current_app.session_factory() as session:
        user = session.scalar(select(User).where(User.username == username))

    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify({"access_token": issue_token(user.id)}), 200
