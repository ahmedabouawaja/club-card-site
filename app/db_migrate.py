"""Lightweight SQLite column adds for existing DBs (create_all won't alter)."""
from sqlalchemy import inspect, text

from app.extensions import db

_LEAD_COLUMNS = {
    "whatsapp": "VARCHAR(30)",
    "address": "VARCHAR(255)",
    "color_hex": "VARCHAR(7)",
    "extras": "TEXT",
}


def ensure_schema() -> None:
    insp = inspect(db.engine)
    if "leads" not in insp.get_table_names():
        return
    existing = {col["name"] for col in insp.get_columns("leads")}
    with db.engine.begin() as conn:
        for name, col_type in _LEAD_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE leads ADD COLUMN {name} {col_type}"))
