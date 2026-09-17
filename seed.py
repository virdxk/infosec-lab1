from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

from app import create_app
from app.models import Post, User

DEMO_USERS = [
    ("admin", "Adm1n-Str0ng-Pass!", "admin"),
    ("alice", "Al1ce-Str0ng-Pass!", "user"),
]

DEMO_POSTS = [
    ("admin", "Welcome", "First post created by the seed script."),
    ("alice", "Notes on JWT", "Access tokens are signed with HS256 and expire in one hour."),
]


def main() -> None:
    app = create_app()
    session = app.session_factory()
    try:
        for username, password, role in DEMO_USERS:
            if session.scalar(select(User).where(User.username == username)):
                continue
            user = User(username=username, role=role)
            user.set_password(password, app.config["BCRYPT_ROUNDS"])
            session.add(user)
        session.commit()

        for username, title, body in DEMO_POSTS:
            author = session.scalar(select(User).where(User.username == username))
            if session.scalar(select(Post).where(Post.title == title)):
                continue
            session.add(Post(author_id=author.id, title=title, body=body))
        session.commit()
        print("seed completed")
    finally:
        session.close()


if __name__ == "__main__":
    main()
