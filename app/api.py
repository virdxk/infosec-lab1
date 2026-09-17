from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select

from app.models import Post
from app.sanitize import clean_post
from app.security import jwt_required

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/data")
@jwt_required
def get_data():
    session = current_app.session_factory()
    try:
        posts = session.scalars(select(Post).order_by(Post.id)).all()
        payload = [clean_post(post) for post in posts]
    finally:
        session.close()

    return jsonify({"count": len(payload), "items": payload}), 200


@bp.post("/posts")
@jwt_required
def create_post():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    body = data.get("body")

    if not isinstance(title, str) or not isinstance(body, str) or not title.strip() or not body.strip():
        return jsonify({"error": "title and body are required"}), 400
    if len(title) > current_app.config["MAX_TITLE_LENGTH"]:
        return jsonify({"error": "title is too long"}), 400
    if len(body) > current_app.config["MAX_BODY_LENGTH"]:
        return jsonify({"error": "body is too long"}), 400

    session = current_app.session_factory()
    try:
        post = Post(author_id=g.current_user_id, title=title.strip(), body=body.strip())
        session.add(post)
        session.commit()
        payload = clean_post(post)
    finally:
        session.close()

    return jsonify(payload), 201
