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

    from .routes import routes
    from .controllers.mensajes import register_socket_events

    app.register_blueprint(routes)
    register_socket_events(socketio)

    from .crear_admin import crear_admin
    app.cli.add_command(crear_admin)

    return app
