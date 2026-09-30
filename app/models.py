import bcrypt
from sqlalchemy import ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(60))

    def set_password(self, password: str, rounds: int) -> None:
        salt = bcrypt.gensalt(rounds=rounds)
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    def check_password(self, password: str) -> bool:
        password_bytes = password.encode()
        # bcrypt raises ValueError on passwords longer than 72 bytes
        if len(password_bytes) > 72:
            return False
        return bcrypt.checkpw(password_bytes, self.password_hash.encode())


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)

    author: Mapped[User] = relationship()


def build_session_factory(database_url: str) -> sessionmaker:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
