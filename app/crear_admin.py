from . import create_app
from .extensions import socketio
from .models import db, User


def crear_administrador(app_instance=None):
    if app_instance is None:
        app_instance = create_app()

    with app_instance.app_context():
        admin = User.query.filter_by(username="Rudeus").first()

        if admin:
            print("⚠️ El usuario administrador ya existe.")
            return

        # Evita duplicar un correo que ya esté registrado.
        usuario_email = User.query.filter_by(email="rudy@gmail.com").first()

        if usuario_email:
            print("⚠️ El correo rudy@gmail.com ya está registrado con otro usuario.")
            return

        admin = User(
            username="Rudeus",
            email="rudy@gmail.com",
            role="admin"
        )
        admin.set_password("password")

        db.session.add(admin)
        db.session.commit()

        print("✅ Usuario administrador creado con éxito.")


if __name__ == "__main__":
    crear_administrador()