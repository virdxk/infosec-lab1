from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

from app import create_app
from app.models import Post, User

USERS = [("alice", "Al1ce-Str0ng-Pass!"), ("bob", "B0b-Str0ng-Pass!")]
POSTS = [("alice", "Welcome", "First post."), ("bob", "Notes on JWT", "Tokens expire in one hour.")]


def main() -> None:
    app = create_app()
    with app.session_factory() as session:
        if session.scalar(select(User)):
            print("database already seeded")
            return

        users = {}
        for username, password in USERS:
            user = User(username=username)
            user.set_password(password, app.config["BCRYPT_ROUNDS"])
            session.add(user)
            users[username] = user
        session.flush()

        for username, title, body in POSTS:
            session.add(Post(author_id=users[username].id, title=title, body=body))
        session.commit()
    print("seed completed")


if __name__ == "__main__":
    main()
