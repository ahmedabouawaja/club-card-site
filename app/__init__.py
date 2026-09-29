import json
import os

from flask import Flask, render_template
from flask_talisman import Talisman
from dotenv import load_dotenv

from app.config import config_by_name
from app.extensions import db, login_manager, csrf, limiter

load_dotenv()

# Content Security Policy: no inline scripts/styles from anywhere but our own
# static files, nothing loaded from a third-party host. Adjust if you add a
# CDN or a payment widget later — never loosen this to 'unsafe-inline' for scripts.
CSP = {
    "default-src": "'self'",
    "img-src": "'self' data: blob:",
    "style-src": "'self' 'unsafe-inline'",
    "style-src-attr": "'unsafe-inline'",
    "script-src": "'self' 'unsafe-eval' 'wasm-unsafe-eval'",
    "font-src": "'self'",
    "connect-src": "'self' https://wa.me",
    "object-src": "'none'",
    "base-uri": "'self'",
    "form-action": "'self' https://wa.me https://api.whatsapp.com",
    "frame-ancestors": "'none'",
}


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "production")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Fail loudly rather than silently running with a weak/missing secret in production.
    if config_name == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Generate one with "
            "`python -c \"import secrets; print(secrets.token_hex(32))\"` "
            "and put it in your .env file before running in production."
        )
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "dev-only-insecure-key-do-not-use-in-production"

    # --- extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Security response headers + forced HTTPS (set force_https=False only for local http dev)
    Talisman(
        app,
        content_security_policy=CSP,
        force_https=config_name == "production",
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        session_cookie_secure=app.config["SESSION_COOKIE_SECURE"],
        referrer_policy="strict-origin-when-cross-origin",
        x_content_type_options=True,
    )

    from app.branding import BENEFITS, TIER_META
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- blueprints ---
    from app.main import bp as main_bp
    from app.auth import bp as auth_bp
    from app.card import bp as card_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(card_bp, url_prefix="/card")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --- error pages (no stack traces or internals ever shown to a visitor) ---
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/error.html", code=403, message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/error.html", code=404, message="Page not found"), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return render_template("errors/error.html", code=429, message="Too many requests — please slow down."), 429

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/error.html", code=500, message="Something went wrong"), 500

    # Defense-in-depth headers Talisman doesn't set by default
    @app.after_request
    def set_extra_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers.pop("Server", None)  # don't advertise the server stack
        return response

    @app.context_processor
    def inject_brand():
        payload = {
            tier: {"title": title, "items": items, "pill": TIER_META[tier]["pill"]}
            for tier, (title, items) in BENEFITS.items()
        }
        return {"benefits_json": json.dumps(payload)}

    with app.app_context():
        db.create_all()
        from app.db_migrate import ensure_schema
        from app.cms import seed_cms_if_empty
        from app.bootstrap import ensure_bootstrap_admin
        ensure_schema()
        seed_cms_if_empty()
        ensure_bootstrap_admin()

    from app.cli import create_admin
    app.cli.add_command(create_admin)

    return app
