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
from flask_login import login_user, logout_user

from ..extensions import db
from ..models import User
from ..utils.validators import validar_contraseña

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("El correo ya está registrado.", "danger")
            return redirect(url_for("auth.register"))

        # Validar la contraseña
        if not validar_contraseña(password):
            flash(
                "La contraseña debe tener al menos 8 caracteres, "
                "una mayúscula, una minúscula y un número.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        # Crear el nuevo usuario con rol "usuario"
        new_user = User(
            username=username,
            email=email,
            role="usuario",
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Usuario registrado con éxito.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

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