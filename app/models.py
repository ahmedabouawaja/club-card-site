import secrets
from datetime import datetime, date

import bcrypt
from flask_login import UserMixin

from app.extensions import db

TIER_CHOICES = ["member", "silver", "gold", "black"]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Login-hardening fields (simple brute-force lockout, no extra service needed)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    card = db.relationship("MembershipCard", backref="owner", uselist=False, cascade="all, delete-orphan")

    # Flask-Login expects `is_active`; we proxy our own column into it.
    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(raw_password.encode("utf-8"), self.password_hash.encode("utf-8"))
        except ValueError:
            return False

    def __repr__(self):
        return f"<User {self.email}>"


class MembershipCard(db.Model):
    __tablename__ = "membership_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    member_no = db.Column(db.String(32), unique=True, nullable=False, index=True)
    tier = db.Column(db.String(16), default="member", nullable=False)
    accent_hex = db.Column(db.String(7), default="#D4FF3A", nullable=False)
    issued_at = db.Column(db.Date, default=date.today, nullable=False)
    valid_until = db.Column(db.Date, nullable=False)
    is_frozen = db.Column(db.Boolean, default=False, nullable=False)  # admin can suspend a card
    # A random, unguessable public token used in QR codes / check-in links —
    # never the sequential DB id, so cards can't be enumerated.
    public_token = db.Column(db.String(48), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))

    def is_expired(self) -> bool:
        return date.today() > self.valid_until


class Lead(db.Model):
    """Quote, callback, personal-card, reader, or custom card-order requests."""
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    kind = db.Column(db.String(24), nullable=False, index=True)  # quote, callback, personal, reader, order
    status = db.Column(db.String(16), default="new", nullable=False)  # new, contacted, closed
    phone = db.Column(db.String(30), nullable=True, index=True)
    whatsapp = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    color_hex = db.Column(db.String(7), nullable=True)
    extras = db.Column(db.Text, nullable=True)  # JSON: nfc, logo, qr, …
    name = db.Column(db.String(120), nullable=True)
    audience = db.Column(db.String(32), nullable=True)  # أعمال / شركات / أفراد
    quantity = db.Column(db.String(32), nullable=True)
    template_name = db.Column(db.String(64), nullable=True)
    line1 = db.Column(db.String(80), nullable=True)
    line2 = db.Column(db.String(80), nullable=True)
    line3 = db.Column(db.String(80), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    place_type = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.String(400), nullable=True)
    image_name = db.Column(db.String(160), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)


class AuditLog(db.Model):
    """Append-only trail of security-relevant events (logins, tier changes, admin actions)."""
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(64), nullable=False)
    detail = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6-safe length


class SiteSetting(db.Model):
    """Simple key/value settings the public site reads (brand, WhatsApp, prices…)."""
    __tablename__ = "site_settings"

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=False, default="")


class CmsItem(db.Model):
    """Editable content blocks: designs, uses, FAQs, reviews, places, chips."""
    __tablename__ = "cms_items"

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(32), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False, default="")
    subtitle = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=True)
    color_a = db.Column(db.String(32), nullable=True)
    color_b = db.Column(db.String(32), nullable=True)
    text_color = db.Column(db.String(32), nullable=True)
    icon = db.Column(db.String(255), nullable=True)
    meta = db.Column(db.String(120), nullable=True)
    page = db.Column(db.String(32), nullable=True, index=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
