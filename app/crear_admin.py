import os
import click

from sqlalchemy.exc import OperationalError

from .utils.validators import validar_contraseña
from .extensions import db
from .models import User


@click.command("crear-admin")
def crear_admin():
    """Crea un usuario administrador de forma interactiva o mediante variables de entorno."""

    username = os.getenv("ADMIN_USERNAME") or click.prompt(
        "Nombre de usuario",
        default="admin",
    )
    email = os.getenv("ADMIN_EMAIL") or click.prompt(
        "Correo del administrador",
    )
    email = email.strip().lower()

    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        password = click.prompt(
            "Contraseña",
            hide_input=True,
            confirmation_prompt=True,
        )

    if not validar_contraseña(password):
        raise click.ClickException(
            "La contraseña debe tener al menos 8 caracteres, "
            "una mayúscula, una minúscula y un número."
        )

    try:
        if User.query.filter_by(username=username).first():
            raise click.ClickException("Ese nombre de usuario ya existe.")

        if User.query.filter_by(email=email).first():
            raise click.ClickException("Ese correo ya está registrado.")

        admin = User(
            username=username,
            email=email,
            role="admin",
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

    except OperationalError as exc:
        db.session.rollback()
        raise click.ClickException(
            "Primero ejecuta: flask --app wsgi db upgrade"
        ) from exc

    click.echo(f"Administrador '{username}' creado correctamente.")