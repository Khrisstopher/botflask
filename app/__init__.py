import os

from flask import Flask

from .config import Config
from .extensions import db, migrate, login_manager, socketio

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import models  # Registra los modelos en SQLAlchemy

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config["CORS_ORIGINS"])

    from .controllers.auth import bp as auth_bp
    from .controllers import errors
    from .controllers.index import bp as main_bp
    from .controllers.post import bp as posts_bp
    from .controllers.users import bp as users_bp
    from .controllers.mensajes import (
        bp as chat_bp,
        register_socket_events,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(chat_bp)

    register_socket_events(socketio)

    from .crear_admin import crear_admin
    app.cli.add_command(crear_admin)

    return app
