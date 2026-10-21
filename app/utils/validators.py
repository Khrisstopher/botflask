
import re

from sqlalchemy import func

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_datos_usuario(username, email):
    """Limpia y valida el nombre de usuario y el correo."""
    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not 3 <= len(username) <= 80:
        return (
            None,
            None,
            "El nombre de usuario debe tener entre 3 y 80 caracteres.",
        )

    if len(email) > 120 or not EMAIL_RE.fullmatch(email):
        return None, None, "Correo electrónico no válido."

    return username, email, None


def usuario_duplicado(username, email, excluir_id=None):
    """Devuelve un mensaje si el nombre o correo ya están registrados."""
    from ..models import User

    consulta_username = User.query.filter(
        User.username == username
    )

    consulta_email = User.query.filter(
        func.lower(User.email) == email
    )

    if excluir_id is not None:
        consulta_username = consulta_username.filter(
            User.id != excluir_id
        )
        consulta_email = consulta_email.filter(
            User.id != excluir_id
        )

    if consulta_username.first():
        return "El nombre de usuario ya está en uso."

    if consulta_email.first():
        return "El correo ya está registrado."

    return None


def validar_contraseña(contraseña):
    """Comprueba que la contraseña cumpla los requisitos mínimos."""
    if not contraseña or len(contraseña) < 8:
        return False

    if not any(caracter.isupper() for caracter in contraseña):
        return False

    if not any(caracter.islower() for caracter in contraseña):
        return False

    if not any(caracter.isdigit() for caracter in contraseña):
        return False

    return True
