from flask import Flask
from .config import Config
from .services.oauth import init_oauth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init oauth
    init_oauth(app)

    # register blueprints
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .public.routes import public_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(public_bp)

    return app