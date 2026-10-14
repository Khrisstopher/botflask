from flask import render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import Post, User, Reaction

@login_required
def feed():
    if request.method == "POST":
        contenido = request.form.get("contenido")
        if contenido:
            nuevo_post = Post(
                contenido=contenido,
                user_id=current_user.id,  # Asegura que se guarde el ID del usuario autenticado
                autor=current_user.username  # Si tienes un campo para el nombre del usuario
            )
            db.session.add(nuevo_post)
            db.session.commit()
            return redirect(url_for("routes.feed"))

    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template("post/feed.html", posts=posts)

@login_required
def reaction(post_id):
    tipo = request.json.get("tipo")

    if tipo not in ["like", "love", "haha", "wow", "sad", "angry"]:
        return jsonify({"error": "Reacción no válida"}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    # Buscar si el usuario ya reaccionó con este tipo de reacción
    reaccion_existente = Reaction.query.filter_by(post_id=post_id, tipo=tipo, user_id=current_user.id).first()

    if reaccion_existente:
        # Si ya existe, eliminar la reacción
        db.session.delete(reaccion_existente)
        mensaje = "Reacción eliminada"
    else:
        # Si no existe, agregar la nueva reacción
        nueva_reaccion = Reaction(tipo=tipo, post_id=post_id, user_id=current_user.id)
        db.session.add(nueva_reaccion)
        mensaje = "Reacción agregada"

    db.session.commit()

    # Contar las reacciones por tipo
    total_reacciones = {t: Reaction.query.filter_by(post_id=post_id, tipo=t).count() for t in ["like", "love", "haha", "wow", "sad", "angry"]}

    return jsonify({"mensaje": mensaje, "reacciones": total_reacciones})