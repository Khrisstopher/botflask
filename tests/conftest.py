import pytest

from app import create_app
from app.config import TestConfig
from app.models import db, User

@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        admin = User(
            username="admin_test",
            email="admin@test.com",
            role="admin",
        )
        admin.set_password("Admin1234")

        db.session.add(admin)
        db.session.commit()

    try:
        yield app
    finally:
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
