# Funciones para el manejo de usuarios

from flask import (
    Blueprint,
    flash,
    redirect,
    abort,
    render_template,
    request,
    jsonify,
    session,
)
from flask_login import current_user, login_required, logout_user

from ..extensions import db
from ..models import User
from sqlalchemy.exc import IntegrityError

from ..utils.validators import (
    validar_contraseña,
    validar_datos_usuario,
    usuario_duplicado,
)

bp = Blueprint("users", __name__)


def obtener_usuarios(formato="html"):
    """Obtiene usuarios para JSON o para renderizar HTML."""
    usuarios = User.query.all()

    if formato == "json":
        return [{"id": u.id, "username": u.username} for u in usuarios]

    return usuarios


@bp.route("/api/usuarios", methods=["GET"])
@login_required
def api_usuarios():
    """API para obtener usuarios en formato JSON."""
    return jsonify(obtener_usuarios(formato="json"))


@bp.route("/usuarios", methods=["GET"])
@login_required
def lista_usuarios():
    """Renderiza la tabla de usuarios en HTML."""
    if current_user.role != "admin":
        abort(401)

    return render_template("users.html", usuarios=obtener_usuarios())



@bp.route("/usuarios/editar/<int:id>", methods=["POST"])
@login_required
def editar_usuario(id):
    """Actualiza los datos de un usuario desde AJAX."""
    usuario = db.session.get(User, id)

    if usuario is None:
        abort(404)

    # Solo el propio usuario o un administrador pueden editar.
    if current_user.role != "admin" and current_user.id != usuario.id:
        abort(401)

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "No se recibieron datos válidos."
        }), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validar y normalizar el nombre de usuario y el correo.
    username, email, error = validar_datos_usuario(
        username,
        email,
    )

    if error:
        return jsonify({"error": error}), 400

    # Comprobar duplicados excluyendo al propio usuario.
    error = usuario_duplicado(
        username,
        email,
        excluir_id=usuario.id,
    )

    if error:
        return jsonify({"error": error}), 400

    # Validar la contraseña solo si se ha proporcionado una nueva.
    if password:
        if not validar_contraseña(password):
            return jsonify({
                "error": (
                    "La contraseña debe tener al menos 8 caracteres, "
                    "una mayúscula, una minúscula y un número."
                )
            }), 400

        usuario.set_password(password)

    # Guardar los datos normalizados.
    usuario.username = username
    usuario.email = email

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": (
                "El nombre de usuario o el correo ya están registrados."
            )
        }), 400

    return jsonify({
        "message": "Usuario actualizado con éxito"
    }), 200


@bp.route("/usuarios/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_usuario(id):
    usuario = db.session.get(User, id)

    if usuario is None:
        abort(404)

    # Un administrador puede eliminar cualquier usuario.
    if current_user.role == "admin":
        nombre_usuario = usuario.username
        es_usuario_actual = current_user.id == id

        db.session.delete(usuario)
        db.session.commit()

        # Si el administrador se elimina a sí mismo, cerrar su sesión.
        if es_usuario_actual:
            logout_user()
            session.clear()
            flash(
                "Tu cuenta ha sido eliminada. Sesión cerrada.",
                "warning",
            )
            return jsonify({
                "message": "Tu cuenta ha sido eliminada. Sesión cerrada."
            }), 200

        flash(
            f"El usuario {nombre_usuario} ha sido eliminado.",
            "success",
        )
        return jsonify({
            "message": f"El usuario {nombre_usuario} ha sido eliminado."
        }), 200

    # Un usuario normal solo puede eliminarse a sí mismo.
    if current_user.id == id:
        db.session.delete(usuario)
        db.session.commit()

        logout_user()
        session.clear()

        flash(
            "Tu cuenta ha sido eliminada. Sesión cerrada.",
            "warning",
        )
        return jsonify({
            "message": "Tu cuenta ha sido eliminada. Sesión cerrada."
        }), 200

    flash("No tienes permisos para eliminar este usuario.", "danger")
    return jsonify({
        "error": "No tienes permisos para eliminar este usuario."
    }), 403


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html", usuarios=current_user)