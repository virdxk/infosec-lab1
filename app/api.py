from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select

from app.middleware import authenticate_request
from app.models import Post
from app.sanitize import serialize_post

api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.before_request(authenticate_request)


@api_bp.get("/data")
def get_data():
    with current_app.session_factory() as session:
        posts = session.scalars(select(Post).order_by(Post.id)).all()
        items = [serialize_post(post) for post in posts]
    return jsonify(items), 200


@api_bp.post("/posts")
def create_post():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    title = data.get("title")
    body = data.get("body")
    if not isinstance(title, str) or not isinstance(body, str) or not title or not body:
        return jsonify({"error": "title and body are required"}), 400

    with current_app.session_factory() as session:
        post = Post(author_id=g.user_id, title=title, body=body)
        session.add(post)
        session.commit()
        return jsonify(serialize_post(post)), 201
