import random
from datetime import datetime

from flask import request
from flask_login import current_user

from app.extensions import db
from app.models import AuditLog


def log_action(action: str, detail: str = None) -> None:
    """Write one audit trail row. Never raises — auditing must not break a request."""
    try:
        entry = AuditLog(
            actor_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            detail=detail,
            ip_address=request.remote_addr,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()


def generate_member_no() -> str:
    """PULSE-1234-5678 style, not sequential, so member numbers aren't guessable/enumerable."""
    block = lambda: "".join(random.choices("0123456789", k=4))
    return f"PULSE-{block()}-{block()}"
