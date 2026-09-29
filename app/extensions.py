"""
Shared extension instances, created here (not bound to an app yet) so
blueprints can import them without circular imports. app/__init__.py
calls .init_app(app) on each one inside the application factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"  # invalidates session if IP/user-agent shifts oddly
