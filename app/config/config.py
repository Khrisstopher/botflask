import os
from dotenv import load_dotenv

load_dotenv()  # lee .env en local; en Render las variables vienen del panel


class Config:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-solo-local"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL", "")
        .replace("postgres://", "postgresql+psycopg2://", 1)
        .replace("postgresql://", "postgresql+psycopg2://", 1)
        or "sqlite:///" + os.path.join(BASE_DIR, "instance", "botflask.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS") or None

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE") == "1"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test"