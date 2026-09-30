from flask import Flask

from app.config import Config
from app.models import build_session_factory


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    if len(app.config["JWT_SECRET"]) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters")

    app.session_factory = build_session_factory(app.config["DATABASE_URL"])

    from app.api import api_bp
    from app.auth import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    return app
