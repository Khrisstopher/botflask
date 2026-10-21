from ..extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)

# Para la mensajería entre usuarios
class Mensaje(db.Model):
    __tablename__ = 'mensaje'
    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=get_utc_now)  # Ahora usa la misma función local

    remitente = db.relationship('User', foreign_keys=[remitente_id], back_populates="mensajes_enviados")
    destinatario = db.relationship('User', foreign_keys=[destinatario_id], back_populates="mensajes_recibidos")

# Usuarios
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    role = db.Column(db.String(20), nullable=False, default="usuario")

    mensajes_enviados = db.relationship(
        'Mensaje',
        foreign_keys=[Mensaje.remitente_id],
        back_populates="remitente",
        cascade="all, delete-orphan"
    )

    mensajes_recibidos = db.relationship(
        'Mensaje',
        foreign_keys=[Mensaje.destinatario_id],
        back_populates="destinatario",
        cascade="all, delete-orphan"
    )

    reacciones = db.relationship(
        'Reaction',
        back_populates='user',
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Cifra la contraseña y la almacena como hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return check_password_hash(self.password_hash, password)

# Publicaciones
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=get_utc_now)
    reacciones = db.relationship('Reaction', back_populates='post', cascade="all, delete-orphan")

    user = db.relationship(
        'User',
        backref=db.backref(
            'posts',
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

# Reacciones a publicaciones
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post = db.relationship('Post', back_populates='reacciones')
    user = db.relationship('User', back_populates='reacciones')
