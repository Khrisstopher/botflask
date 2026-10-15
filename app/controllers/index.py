from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.app_errorhandler(401)
def handle_401(error):
    return render_template("401.html"), 401


@bp.app_errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404


@bp.route("/favicon.ico")
def favicon():
    return "", 204
