import os

import click

from .models import db, User


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

    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        password = click.prompt(
            "Contraseña",
            hide_input=True,
            confirmation_prompt=True,
        )

    # Validar la regla mínima de contraseña.
    if not any(char.isupper() for char in password) or not any(
        char.isdigit() for char in password
    ):
        raise click.ClickException(
            "La contraseña debe contener al menos una mayúscula y un número."
        )

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

    click.echo(f"Administrador '{username}' creado correctamente.")
