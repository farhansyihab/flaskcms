import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config, ProductionConfig
from .services.oauth import init_oauth


def create_app():
    env = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # =====================
    # Config
    # =====================
    if env == "production":
        app.config.from_object(ProductionConfig)
        app.config["PREFERRED_URL_SCHEME"] = "https"
        app.config["SERVER_NAME"] = os.getenv("SERVER_NAME")
    else:
        app.config.from_object(Config)

    # =====================
    # OAuth
    # =====================
    init_oauth(app)

    # =====================
    # Blueprints
    # =====================
    from .auth.routes import auth_bp
    from .admin import admin_bp      # ← PERUBAHAN PENTING
    from .public import public_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(public_bp)

    # =====================
    # ProxyFix (Production)
    # =====================
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )

    return app