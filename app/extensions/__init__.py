from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = (
    "Por favor, inicia sesión para acceder a esta página."
)
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    from ..models import User

    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
