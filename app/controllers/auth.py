# Funciones para la autenticación de usuario en el sistema.

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
)

from sqlalchemy.exc import IntegrityError

from ..utils.validators import (
    validar_contraseña,
    validar_datos_usuario,
    usuario_duplicado,
)

from flask_login import login_user, logout_user

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username, email, error = validar_datos_usuario(
            request.form.get("username"),
            request.form.get("email"),
        )

        # Validar los campos antes de consultar la base de datos.
        if not error:
            error = usuario_duplicado(username, email)

        if error:
            flash(error, "danger")
            return redirect(url_for("auth.register"))

        # Obtener la contraseña de forma segura si falta el campo.
        password = request.form.get("password", "")

        if not validar_contraseña(password):
            flash(
                "La contraseña debe tener al menos 8 caracteres, "
                "una mayúscula, una minúscula y un número.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        # Crear el nuevo usuario.
        new_user = User(
            username=username,
            email=email,
            role="usuario",
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash(
                "El usuario o el correo ya existen.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        flash("Usuario registrado con éxito.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("_flashes", None)
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))