from flask import render_template

from .index import bp


@bp.app_errorhandler(401)
def handle_401(error):
    return render_template("401.html"), 401


@bp.app_errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404


@bp.route("/favicon.ico")
def favicon():
    return "", 204