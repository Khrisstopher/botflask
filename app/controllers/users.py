# Funciones para el manejo de usuarios

from flask import flash, redirect, abort, render_template, request, jsonify, session
from flask_login import current_user, login_required, logout_user
from ..extensions import db
from ..models import User
from ..utils.validators import validar_contraseña

# Funcion para obtener usuarios
def obtener_usuarios(formato="html"):
    """Obtiene la lista de usuarios, devolviendo JSON o datos para renderizar"""
    usuarios = User.query.all()
    
    if formato == "json":
        return [{"id": u.id, "username": u.username} for u in usuarios]
    
    return usuarios  # Devuelve la lista de objetos User para renderizar HTML

@login_required
def api_usuarios():
    """API para obtener usuarios en formato JSON"""
    return jsonify(obtener_usuarios(formato="json"))

@login_required
def lista_usuarios():
    """Renderiza la tabla de usuarios en HTML"""
    
    if not current_user.role == "admin":
        abort(401)
    
    return render_template("users.html", usuarios=obtener_usuarios())

@login_required
def editar_usuario(id):
    """Permite actualizar los datos de un usuario desde AJAX."""
    usuario = User.query.get_or_404(id)

    # Solo el propio usuario o un administrador pueden editar
    if current_user.role != "admin" and current_user.id != usuario.id:
        abort(401)

    data = request.get_json()
    #print("Datos recibidos en JSON:", data)

    if not data or all(value in [None, ""] for value in data.values()):
        print("No se recibieron datos o están vacíos.")  
        return jsonify({"error": "No se recibieron datos o están vacíos"}), 400


    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validar si el correo ya está en uso por otro usuario
    usuario_existente = User.query.filter(User.email == email, User.id != id).first()
    if usuario_existente:
        return jsonify({"error": "Este correo ya está en uso por otro usuario"}), 400

    usuario.username = username
    usuario.email = email

    # Solo actualizar la contraseña si se ingresó una nueva
    if password:
        if not validar_contraseña(password):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número."}), 400
        usuario.set_password(password)

    db.session.commit()
    return jsonify({"message": "Usuario actualizado con éxito"}), 200

@login_required
def eliminar_usuario(id):
    usuario = User.query.get_or_404(id)

    # Si el usuario actual es admin, puede eliminar cualquier usuario
    if current_user.role == "admin":
        db.session.delete(usuario)
        db.session.commit()

        # Si el admin se elimina a sí mismo, cerrar su sesión
        if current_user.id == id:
            logout_user()
            session.clear()
            flash("Tu cuenta ha sido eliminada. Sesión cerrada.", "warning")
            return jsonify({"message": "Tu cuenta ha sido eliminada. Sesión cerrada."}), 200

        flash(f"El usuario {usuario.username} ha sido eliminado.", "success")
        return jsonify({"message": f"El usuario {usuario.username} ha sido eliminado."}), 200

    # Si el usuario NO es admin, solo puede eliminarse a sí mismo
    elif current_user.id == id:
        db.session.delete(usuario)
        db.session.commit()
        logout_user()
        session.clear()
        flash("Tu cuenta ha sido eliminada. Sesión cerrada.", "warning")
        return jsonify({"message": "Tu cuenta ha sido eliminada. Sesión cerrada."}), 200

    # Si no es admin y quiere eliminar a otro, se le niega el permiso
    else:
        flash("No tienes permisos para eliminar este usuario.", "danger")
        return jsonify({"error": "No tienes permisos para eliminar este usuario."}), 403  

# Maneja la vista del perfil de usuario
@login_required
def profile():
    return render_template("profile.html", usuarios=current_user)