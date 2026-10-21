from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
)

from flask_wtf.csrf import CSRFError

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(error):
    if request.is_json or request.headers.get("X-Requested-With"):
        return jsonify({
            "error": "Token CSRF inválido o expirado. Recarga la página."
        }), 400

    flash("El formulario expiró. Inténtalo de nuevo.", "warning")
    return redirect(url_for("main.index"))


@bp.app_errorhandler(401)
def handle_401(error):
    return render_template("401.html"), 401


@bp.app_errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404


@bp.route("/favicon.ico")
def favicon():
    return "", 204
