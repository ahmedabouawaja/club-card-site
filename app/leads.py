import json
import re
import secrets
from pathlib import Path

from flask import current_app, request
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Lead
from app.utils import log_action

PHONE_RE = re.compile(r"^(?:\+?20|0)?1[0125]\d{8}$")
KINDS = {"quote", "callback", "personal", "reader", "order"}
ALLOWED_IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
EXTRA_KEYS = ("nfc", "logo", "qr", "name_print", "gloss", "matte")
LOGO_MODES = {"badge", "cover"}
LOGO_POS = {"center", "top-right", "top-left", "bottom-right", "bottom-left"}
LOGO_SIZES = {"sm", "md", "lg"}


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D+", "", raw or "")
    if digits.startswith("20") and len(digits) == 12:
        digits = "0" + digits[2:]
    if not PHONE_RE.match(digits):
        return None
    return digits


def _save_image(file_storage) -> str | None:
    if file_storage is None or not file_storage.filename:
        return None
    suffix = Path(file_storage.filename).suffix.lower()
    if suffix not in ALLOWED_IMG:
        raise ValueError("ارفع صورة PNG أو JPG أو WEBP أو GIF.")
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > 2 * 1024 * 1024:
        raise ValueError("حجم الصورة أكبر من 2 ميجا.")
    folder = Path(current_app.instance_path) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    name = secrets.token_urlsafe(16) + suffix
    dest = folder / name
    file_storage.save(dest)
    return name


def _parse_extras(raw) -> str | None:
    if raw is None or raw == "":
        return None
    data = raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return raw[:400]
    if not isinstance(data, dict):
        return None
    cleaned = {k: bool(data.get(k)) for k in EXTRA_KEYS if k in data}
    if cleaned.get("logo"):
        mode = str(data.get("logo_mode") or "badge")
        pos = str(data.get("logo_pos") or "center")
        size = str(data.get("logo_size") or "md")
        cleaned["logo_mode"] = mode if mode in LOGO_MODES else "badge"
        cleaned["logo_pos"] = pos if pos in LOGO_POS else "center"
        cleaned["logo_size"] = size if size in LOGO_SIZES else "md"
    return json.dumps(cleaned, ensure_ascii=False) if cleaned else None


def create_lead(kind: str) -> tuple[dict, int]:
    if kind not in KINDS:
        return {"ok": False, "error": "نوع الطلب غير صحيح."}, 400

    data = request.get_json(silent=True) or {}
    form = request.form

    def field(name, default=""):
        if request.is_json:
            return str(data.get(name) or default).strip()
        return str(form.get(name) or default).strip()

    phone = normalize_phone(field("phone"))
    whatsapp = normalize_phone(field("whatsapp")) or phone

    if kind in {"callback", "personal", "order"} and not phone:
        return {"ok": False, "error": "أدخل رقم موبايل مصري صحيح."}, 400

    if kind == "order":
        if not whatsapp:
            return {"ok": False, "error": "أدخل رقم واتساب صحيح."}, 400
        address = field("address")
        if len(address) < 5:
            return {"ok": False, "error": "اكتب العنوان بالتفصيل."}, 400
        qty = field("quantity")
        if not qty:
            return {"ok": False, "error": "حدد الكمية المطلوبة."}, 400

    color = field("color") or field("color_hex")
    if color and not HEX_RE.match(color):
        color = None

    extras_raw = data.get("extras") if request.is_json else form.get("extras")
    extras = _parse_extras(extras_raw)

    try:
        image_name = None if request.is_json else _save_image(request.files.get("image"))
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}, 400

    lead = Lead(
        kind=kind,
        phone=phone,
        whatsapp=whatsapp if kind == "order" else None,
        address=(field("address")[:255] or None) if kind == "order" else None,
        color_hex=color,
        extras=extras,
        name=field("name")[:120] or None,
        audience=field("audience")[:32] or None,
        quantity=field("quantity")[:32] or None,
        template_name=field("template")[:64] or None,
        line1=field("line1")[:80] or None,
        line2=field("line2")[:80] or None,
        line3=field("line3")[:80] or None,
        link=field("link")[:255] or None,
        place_type=field("place")[:64] or None,
        notes=field("notes")[:400] or None,
        image_name=image_name,
        ip_address=request.remote_addr,
    )
    db.session.add(lead)
    db.session.commit()
    log_action("lead_" + kind, detail=f"lead_id={lead.id} phone={phone or '-'}")
    return {"ok": True, "id": lead.id}, 201
