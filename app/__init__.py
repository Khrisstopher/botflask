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
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    from .routes import routes
    from .controllers.mensajes import register_socket_events

    app.register_blueprint(routes)
    register_socket_events(socketio)

    with app.app_context():
        db.create_all()

    from .crear_admin import crear_admin
    app.cli.add_command(crear_admin)

    return app
