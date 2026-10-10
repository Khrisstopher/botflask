from flask import render_template, redirect, url_for
from flask_login import current_user

def handle_401(error):
    return render_template("401.html"), 401

def handle_404(error):
    return render_template("404.html"), 404

def favicon():
    return "", 204 
