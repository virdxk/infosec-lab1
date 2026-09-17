from flask import Flask, jsonify

from app.config import Config, validate
from app.models import build_session_factory


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    validate(app.config)

    engine, session_factory = build_session_factory(app.config["DATABASE_URL"])
    app.engine = engine
    app.session_factory = session_factory

    from app.api import bp as api_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "internal server error"}), 500

    return app
