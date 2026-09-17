from markupsafe import escape


def clean(value: str | None) -> str:
    if value is None:
        return ""
    return str(escape(value))


def clean_post(post) -> dict:
    return {
        "id": post.id,
        "title": clean(post.title),
        "body": clean(post.body),
        "author": clean(post.author.username),
        "created_at": post.created_at.isoformat(),
    }
