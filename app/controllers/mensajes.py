from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user
from ..models import db
from ..models.models import Mensaje

def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect(auth=None):
        if not current_user.is_authenticated:
            disconnect()
            return
        print(f"✅ Usuario {current_user.id} conectado")
        
        # Unir al usuario a todas sus salas activas
        for chat_id in obtener_chats_usuario(current_user.id):
            join_room(chat_id)
            print(f"🔵 Usuario {current_user.id} se unió a la sala {chat_id}")

    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            print(f"❌ Usuario {current_user.id} desconectado")
        else:
            print("❌ Usuario no autenticado desconectado")

    @socketio.on('join_chat')
    def join_chat(data):
        """ El usuario se une a un chat con otro usuario """
        other_user_id = data.get('other_user_id')
        if other_user_id:
            room = f"chat_{min(current_user.id, other_user_id)}_{max(current_user.id, other_user_id)}"
            join_room(room)
            print(f"🔵 Usuario {current_user.id} se unió a la sala {room}")

    @socketio.on('send_message')
    def handle_message(data):
        destinatario_id = data.get('destinatario_id')
        message = data.get('message')

        if not destinatario_id or not message:
            return

        destinatario_id = int(destinatario_id)

        # Guardar en la base de datos
        new_message = Mensaje(remitente_id=current_user.id, destinatario_id=destinatario_id, contenido=message)
        db.session.add(new_message)
        db.session.commit()
        print(f"📝 Mensaje guardado en la BD: {new_message.contenido}")

        # Obtener la sala correcta
        room = f"chat_{min(current_user.id, destinatario_id)}_{max(current_user.id, destinatario_id)}"
        print(f"📤 Intentando enviar mensaje a la sala: {room}")

        # Emitir el mensaje
        socketio.emit('receive_message', {
            'remitente_id': current_user.id,
            'message': message
        }, to=room)

        print(f"✅ Mensaje enviado de {current_user.id} a {destinatario_id}: {message}")

def obtener_chats_usuario(user_id):
    """ Función para obtener todas las salas en las que el usuario debería estar """
    chats = db.session.query(Mensaje).filter(
        (Mensaje.remitente_id == user_id) | (Mensaje.destinatario_id == user_id)
    ).all()
    
    rooms = set()
    for msg in chats:
        chat_id = f"chat_{min(msg.remitente_id, msg.destinatario_id)}_{max(msg.remitente_id, msg.destinatario_id)}"
        rooms.add(chat_id)
    
    return rooms


from flask import jsonify
from flask_login import login_required

@login_required
def obtener_mensajes(otro_usuario_id):
    mensajes = Mensaje.query.filter(
        ((Mensaje.remitente_id == current_user.id) & (Mensaje.destinatario_id == otro_usuario_id)) |
        ((Mensaje.remitente_id == otro_usuario_id) & (Mensaje.destinatario_id == current_user.id))
    ).order_by(Mensaje.fecha_envio).all()

    return jsonify([{
        "remitente_id": m.remitente_id,
        "destinatario_id": m.destinatario_id,
        "texto": m.contenido,
        "fecha_envio": m.fecha_envio.isoformat()
    } for m in mensajes])
