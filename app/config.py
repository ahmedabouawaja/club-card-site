import os
from datetime import timedelta


def _bool_env(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Config:
    """
    Base config. Nothing sensitive has a hardcoded fallback for production —
    the app refuses to start in production without a real SECRET_KEY (see app/__init__.py).
    """

    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///club.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Session / cookie hardening ---
    SESSION_COOKIE_HTTPONLY = True          # JS can never read the session cookie
    SESSION_COOKIE_SAMESITE = "Lax"         # blocks most cross-site request forgery vectors
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)  # cookie only sent over HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # --- CSRF (Flask-WTF) ---
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # tokens tied to session, not a fixed expiry

    # --- Uploads (e.g. a member photo later) ---
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB hard cap on any request body

    # --- Rate limiting ---
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # --- Misc ---
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")


class DevelopmentConfig(Config):
    DEBUG = True
    # Local dev over plain http: allow a non-secure cookie so login works without HTTPS.
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", False)
    REMEMBER_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", False)


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "testing-only-not-secret"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
