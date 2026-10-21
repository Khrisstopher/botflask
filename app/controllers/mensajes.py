from flask import Blueprint, jsonify, current_app
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, disconnect
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Mensaje, User

bp = Blueprint("chat", __name__)


def register_socket_events(socketio):
    @socketio.on("connect")
    def handle_connect(auth=None):
        if not current_user.is_authenticated:
            disconnect()
            return

        current_app.logger.info(
            "Usuario %s conectado", current_user.id
        )

        # Unir al usuario a sus salas de chat activas.
        for chat_id in obtener_chats_usuario(current_user.id):
            join_room(chat_id)
            current_app.logger.debug(
                "Usuario %s se unió a la sala %s",
                current_user.id,
                chat_id,
            )

    @socketio.on("disconnect")
    def handle_disconnect():
        if current_user.is_authenticated:
            current_app.logger.info(
                "Usuario %s desconectado", current_user.id
            )
        else:
            current_app.logger.info(
                "Usuario no autenticado desconectado"
            )

    @socketio.on("join_chat")
    def join_chat(data):
        """Unir al usuario autenticado a una sala de chat."""
        if not current_user.is_authenticated:
            disconnect()
            return

        if not isinstance(data, dict):
            emit("error_mensaje", {
                "error": "Los datos del chat no son válidos."
            })
            return

        try:
            other_user_id = int(data.get("other_user_id"))
        except (TypeError, ValueError):
            emit("error_mensaje", {
                "error": "El identificador del usuario no es válido."
            })
            return

        if other_user_id <= 0:
            emit("error_mensaje", {
                "error": "El identificador del usuario no es válido."
            })
            return

        if other_user_id == current_user.id:
            emit("error_mensaje", {
                "error": "No puedes abrir un chat contigo mismo."
            })
            return

        # Comprobar que el otro usuario existe.
        destinatario = db.session.get(User, other_user_id)
        if destinatario is None:
            emit("error_mensaje", {
                "error": "El destinatario no existe."
            })
            return

        room = (
            f"chat_{min(current_user.id, other_user_id)}_"
            f"{max(current_user.id, other_user_id)}"
        )

        join_room(room)
        current_app.logger.debug(
            "Usuario %s se unió a la sala %s",
            current_user.id,
            room,
        )

    @socketio.on("send_message")
    def handle_message(data):
        if not current_user.is_authenticated:
            disconnect()
            return

        if not isinstance(data, dict):
            emit("error_mensaje", {
                "error": "Los datos del mensaje no son válidos."
            })
            return

        try:
            destinatario_id = int(data.get("destinatario_id"))
        except (TypeError, ValueError):
            emit("error_mensaje", {
                "error": "El identificador del destinatario no es válido."
            })
            return

        if destinatario_id <= 0:
            emit("error_mensaje", {
                "error": "El identificador del destinatario no es válido."
            })
            return

        if destinatario_id == current_user.id:
            emit("error_mensaje", {
                "error": "No puedes enviarte mensajes a ti mismo."
            })
            return

        message = data.get("message")

        if not isinstance(message, str):
            emit("error_mensaje", {
                "error": "El mensaje debe ser texto."
            })
            return

        message = message.strip()

        if not message:
            emit("error_mensaje", {
                "error": "El mensaje no puede estar vacío."
            })
            return

        if len(message) > 5000:
            emit("error_mensaje", {
                "error": "El mensaje no puede superar los 5000 caracteres."
            })
            return

        # Comprobar que el destinatario exista antes de guardar.
        destinatario = db.session.get(User, destinatario_id)
        if destinatario is None:
            emit("error_mensaje", {
                "error": "El destinatario no existe."
            })
            return

        # Guardar el mensaje y manejar posibles errores de integridad.
        new_message = Mensaje(
            remitente_id=current_user.id,
            destinatario_id=destinatario_id,
            contenido=message,
        )

        try:
            db.session.add(new_message)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            current_app.logger.warning(
                "Error de integridad al guardar el mensaje "
                "del usuario %s al usuario %s",
                current_user.id,
                destinatario_id,
            )
            emit("error_mensaje", {
                "error": "No se pudo guardar el mensaje. "
                         "Comprueba los datos e inténtalo de nuevo."
            })
            return

        current_app.logger.info(
            "Mensaje guardado en la BD. Remitente: %s, destinatario: %s",
            current_user.id,
            destinatario_id,
        )

        # Obtener la sala correspondiente a ambos usuarios.
        room = (
            f"chat_{min(current_user.id, destinatario_id)}_"
            f"{max(current_user.id, destinatario_id)}"
        )

        current_app.logger.debug(
            "Intentando enviar mensaje a la sala: %s", room
        )

        socketio.emit(
            "receive_message",
            {
                "remitente_id": current_user.id,
                "message": message,
            },
            to=room,
        )

        current_app.logger.info(
            "Mensaje enviado de %s a %s",
            current_user.id,
            destinatario_id,
        )


def obtener_chats_usuario(user_id):
    """Obtiene las salas de chat del usuario."""
    chats = db.session.query(Mensaje).filter(
        (Mensaje.remitente_id == user_id)
        | (Mensaje.destinatario_id == user_id)
    ).all()

    rooms = set()

    for msg in chats:
        chat_id = (
            f"chat_{min(msg.remitente_id, msg.destinatario_id)}_"
            f"{max(msg.remitente_id, msg.destinatario_id)}"
        )
        rooms.add(chat_id)

    return rooms


@bp.route("/api/mensajes/<int:otro_usuario_id>", methods=["GET"])
@login_required
def obtener_mensajes(otro_usuario_id):
    mensajes = Mensaje.query.filter(
        (
            (Mensaje.remitente_id == current_user.id)
            & (Mensaje.destinatario_id == otro_usuario_id)
        )
        | (
            (Mensaje.remitente_id == otro_usuario_id)
            & (Mensaje.destinatario_id == current_user.id)
        )
    ).order_by(Mensaje.fecha_envio).all()

    return jsonify([
        {
            "remitente_id": m.remitente_id,
            "destinatario_id": m.destinatario_id,
            "texto": m.contenido,
            "fecha_envio": m.fecha_envio.isoformat(),
        }
        for m in mensajes
    ])