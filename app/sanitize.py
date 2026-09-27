from markupsafe import escape

from app.models import Post


def serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "title": str(escape(post.title)),
        "body": str(escape(post.body)),
        "author": str(escape(post.author.username)),
        "created_at": post.created_at.isoformat(),
    }
