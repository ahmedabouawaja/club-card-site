"""Create a starter admin from env vars on first boot (hosting / deploys)."""
import os

from app.extensions import db
from app.models import User


def ensure_bootstrap_admin() -> None:
    email = (os.environ.get("BOOTSTRAP_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL") or "").strip()
    password = (os.environ.get("BOOTSTRAP_ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or "").strip()
    name = (os.environ.get("BOOTSTRAP_ADMIN_NAME") or "Admin").strip() or "Admin"
    if not email or not password:
        return
    existing = User.query.filter_by(email=email.lower()).first()
    if existing:
        return
    user = User(name=name, email=email.lower(), is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
