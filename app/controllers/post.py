from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Post, Reaction

bp = Blueprint("posts", __name__)

TIPOS_REACCION = ["like", "love", "haha", "wow", "sad", "angry"]


@bp.route("/feed", methods=["GET", "POST"])
@login_required
def feed():
    if request.method == "POST":
        contenido = request.form.get("contenido")

        if contenido:
            nuevo_post = Post(
                contenido=contenido,
                user_id=current_user.id
            )
            db.session.add(nuevo_post)
            db.session.commit()

            return redirect(url_for("posts.feed"))

    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()

    # Calcular los conteos de reacciones para cada publicación
    for post in posts:
        conteos = {tipo: 0 for tipo in TIPOS_REACCION}

        for reaccion in post.reacciones:
            if reaccion.tipo in conteos:
                conteos[reaccion.tipo] += 1

        post.reaction_counts = conteos
        
    return render_template("post/feed.html", posts=posts, TIPOS_REACCION=TIPOS_REACCION)


@bp.route("/reaction/<int:post_id>", methods=["POST"])
@login_required
def reaction(post_id):
    datos = request.get_json(silent=True) or {}
    tipo = datos.get("tipo")

    if tipo not in TIPOS_REACCION:
        return jsonify({"error": "Reacción no válida"}), 400

    post = db.session.get(Post, post_id)

    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    reaccion_existente = Reaction.query.filter_by(
        post_id=post_id,
        tipo=tipo,
        user_id=current_user.id,
    ).first()

    if reaccion_existente:
        db.session.delete(reaccion_existente)
        mensaje = "Reacción eliminada"
    else:
        nueva_reaccion = Reaction(
            tipo=tipo,
            post_id=post_id,
            user_id=current_user.id,
        )
        db.session.add(nueva_reaccion)
        mensaje = "Reacción agregada"

    db.session.commit()

    total_reacciones = {
        t: Reaction.query.filter_by(post_id=post_id, tipo=t).count()
        for t in TIPOS_REACCION
    }

    return jsonify({
        "mensaje": mensaje,
        "reacciones": total_reacciones,
    })