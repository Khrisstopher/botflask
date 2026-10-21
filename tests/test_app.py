
from app.extensions import db, socketio
from app.models import User, Mensaje


def test_01_disponibilidad_ruta_principal(client):
    """Validar que la ruta principal responda HTTP 200 o 302."""
    response = client.get("/")
    assert response.status_code in [200, 302]


def test_02_carga_vista_autenticacion(client):
    """Validar el acceso a la vista de login."""
    response = client.get("/login")
    assert response.status_code == 200

def test_03_rechaza_credenciales_invalidas(client):
    """El login debe rechazar credenciales incorrectas."""
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "ContraseñaIncorrecta123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # El usuario no debe quedar autenticado.
    with client.session_transaction() as session:
        assert not session.get("_user_id")


def test_04_acepta_credenciales_validas(client):
    """El login debe aceptar las credenciales del usuario de prueba."""
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "Admin1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # El usuario debe quedar autenticado.
    with client.session_transaction() as session:
        assert session.get("_user_id")

def test_usa_base_de_datos_temporal(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"

    with app.app_context():
        assert db.engine.url.database == ":memory:"

def test_registro_rechaza_contraseña_invalida(client, app):
    """No debe registrar usuarios con contraseñas inválidas."""
    response = client.post(
        "/register",
        data={
            "username": "usuario_invalido",
            "email": "invalido@test.com",
            "password": "Ab1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        usuario = User.query.filter_by(
            email="invalido@test.com"
        ).first()
        assert usuario is None


def test_registro_acepta_contraseña_valida(client, app):
    """Debe registrar usuarios con contraseñas válidas."""
    response = client.post(
        "/register",
        data={
            "username": "usuario_valido",
            "email": "valido@test.com",
            "password": "Abcdefg1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        usuario = User.query.filter_by(
            email="valido@test.com"
        ).first()

        assert usuario is not None
        assert usuario.username == "usuario_valido"
        assert usuario.check_password("Abcdefg1")



def test_post_sin_token_csrf_es_rechazado(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    # Intentar iniciar sesión sin enviar el token CSRF.
    client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "Admin1234",
        },
    )

    # Si no inició sesión, debe redirigir al login al acceder al feed.
    r = client.get("/feed")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_logout_solo_acepta_post(app):
    client = app.test_client()

    response = client.get("/logout")

    assert response.status_code == 405


def test_registro_rechaza_username_repetido(client):
    r = client.post("/register", data={
        "username": "admin_test", "email": "otro@test.com", "password": "Abcd1234"})
    assert r.status_code == 302 and "/register" in r.headers["Location"]  # sin 500

def test_registro_rechaza_username_en_blanco(client):
    r = client.post("/register", data={
        "username": "   ", "email": "nuevo@test.com", "password": "Abcd1234"})
    assert r.status_code == 302 and "/register" in r.headers["Location"]


def test_editar_usuario_rechaza_username_repetido(client, app):
    """No debe permitir editar un usuario con el username de otro."""

    with app.app_context():
        usuario = User.query.filter_by(username="admin_test").first()
        assert usuario is not None

        otro_usuario = User(
            username="otro_usuario",
            email="otro_usuario@test.com",
        )
        otro_usuario.set_password("Abcd1234")
        db.session.add(otro_usuario)
        db.session.commit()

        usuario_id = usuario.id
        username_repetido = otro_usuario.username
        email_original = usuario.email

    # Iniciar sesión como administrador.
    client.post("/login", data={
        "email": "admin@test.com",
        "password": "Admin1234",
    })

    response = client.post(
        f"/usuarios/editar/{usuario_id}",
        json={
            "username": username_repetido,
            "email": email_original,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_chat_rechaza_destinatario_inexistente(client, app):
    """No debe guardar mensajes dirigidos a usuarios inexistentes."""

    # Iniciar sesión con el usuario de prueba.
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "Admin1234",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(User, 9999) is None
        mensajes_antes = Mensaje.query.count()

    # Conectar Socket.IO usando la sesión autenticada.
    ws = socketio.test_client(
        app,
        flask_test_client=client,
    )
    assert ws.is_connected()

    # Intentar enviar un mensaje a un destinatario inexistente.
    ws.emit(
        "send_message",
        {
            "destinatario_id": 9999,
            "message": "hola",
        },
    )

    # El servidor debe notificar el rechazo al emisor.
    eventos = ws.get_received()

    assert any(
        evento["name"] == "error_mensaje"
        and evento["args"][0].get("error")
        == "El destinatario no existe."
        for evento in eventos
    )

    # No debe haberse guardado ningún mensaje adicional.
    with app.app_context():
        assert Mensaje.query.count() == mensajes_antes

    ws.disconnect()


def test_eliminar_usuario_borra_todo_lo_que_creo(client, app):
    from app.extensions import db
    from app.models import User, Post, Reaction, Mensaje

    with app.app_context():
        otro = User(username="otro", email="otro@test.com")
        otro.set_password("Abcd1234")
        db.session.add(otro)
        db.session.commit()
        admin = User.query.filter_by(username="admin_test").first()
        post_admin = Post(user_id=admin.id, contenido="del admin")
        post_otro = Post(user_id=otro.id, contenido="del otro")
        db.session.add_all([post_admin, post_otro])
        db.session.commit()
        db.session.add_all([
            Reaction(tipo="like", post_id=post_admin.id, user_id=otro.id),
            Mensaje(remitente_id=otro.id, destinatario_id=admin.id, contenido="hola"),
        ])
        db.session.commit()
        otro_id = otro.id

    client.post("/login", data={"email": "admin@test.com", "password": "Admin1234"})
    assert client.post(f"/usuarios/eliminar/{otro_id}").status_code == 200

    with app.app_context():
        assert db.session.get(User, otro_id) is None
        assert Post.query.filter_by(user_id=otro_id).count() == 0
        assert Reaction.query.filter_by(user_id=otro_id).count() == 0
        assert Mensaje.query.count() == 0