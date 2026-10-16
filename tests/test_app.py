from app.extensions import db
from app.models import User

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
