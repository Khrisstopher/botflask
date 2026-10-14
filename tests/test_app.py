def test_01_disponibilidad_ruta_principal(client):
    """Validar que la ruta principal responda HTTP 200 o 302."""
    response = client.get("/")
    assert response.status_code in [200, 302]


def test_02_carga_vista_autenticacion(client):
    """Validar el acceso a la vista de login."""
    response = client.get("/login")
    assert response.status_code == 200


def test_03_validacion_credenciales_invalidas(client):
    """Validar respuesta ante login con credenciales erróneas."""
    response = client.post(
        "/login",
        data={
            "username": "usuario_inexistente",
            "password": "password_falso",
        },
        follow_redirects=True,
    )
    assert response.status_code in [200, 400]

from app.models import db

def test_usa_base_de_datos_temporal(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"

    with app.app_context():
        assert db.engine.url.database == ":memory:"