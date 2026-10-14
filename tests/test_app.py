
import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import db, User

@pytest.fixture # Prepara el entorno
def client():
    app = create_app()
    app.config['TESTING'] = True # Modo de prueba
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username="Rudeus").first()

        if not admin:
            admin = User.query.filter_by(email="rudy@gmail.com").first()

        if not admin:
            admin = User(
                username="Rudeus",
                email="rudy@gmail.com",
                role="admin"
            )
            admin.set_password("password")
            db.session.add(admin)
            db.session.commit()

    with app.test_client() as client:
        yield client

def test_01_disponibilidad_ruta_principal(client):
    """Caso de Prueba 1: Validar que la ruta principal responda HTTP 200 o 302."""
    response = client.get('/')
    assert response.status_code in [200, 302]

def test_02_carga_vista_autenticacion(client):
    """Caso de Prueba 2: Validar el acceso a la vista de login."""
    response = client.get('/login')
    assert response.status_code == 200

def test_03_validacion_credenciales_invalidas(client):
    """Caso de Prueba 3: Validar respuesta ante login con credenciales erróneas."""
    response = client.post('/login', data=dict(
        username='usuario_inexistente',
        password='password_falso'
    ), follow_redirects=True)
    assert response.status_code in [200, 400]