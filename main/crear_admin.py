import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask
from models.models import db, User
from config import Config

def crear_administrador(app_instance=None):
    # Si no recibe una app (por ejemplo, al ejecutar el script directamente), crea una
    if app_instance is None:
        app_instance = Flask(__name__)
        app_instance.config.from_object(Config)
        
        INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        DB_FILE_PATH = os.path.join(INSTANCE_DIR, 'botflask.db')
        app_instance.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE_PATH}"
        
        db.init_app(app_instance)

    with app_instance.app_context():
        admin = User.query.filter_by(username="Rudeus").first()
        if admin:
            print("⚠️ El usuario administrador ya existe.")
        else:
            admin = User(
                username="Rudeus",
                email="rudy@gmail.com",
                role="admin"
            )
            admin.set_password("Hola1234")
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado con éxito.")

if __name__ == '__main__':
    crear_administrador()