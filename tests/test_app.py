import sys
import os
import pytest

# Agregar la carpeta raíz para importar módulos de 'main'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main.app import app
from main.models import db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            # Asegura que las tablas existan
            db.create_all()
            
            # Crea el admin solo si no existe
            if not User.query.filter_by(username="Rudeus").first():
                admin = User(username="Rudeus", email="rudy@gmail.com", role="admin")
                admin.set_password("Hola1234")
                db.session.add(admin)
                db.session.commit()
                
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