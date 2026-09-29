import json
import re
from datetime import date, timedelta
from functools import wraps

from email_validator import EmailNotValidError, validate_email
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app.admin import bp
from app.branding import ACCENTS, BENEFITS, TIER_META, accent_hex, accent_id, present_card
from app.extensions import db
from app.models import User, MembershipCard, Lead, TIER_CHOICES
from app.utils import generate_member_no, log_action

_EXTRA_LABELS = {
    "nfc": "NFC",
    "logo": "صورة / لوجو",
    "qr": "QR",
    "name_print": "اسم مطبوع",
    "gloss": "لامع",
    "matte": "مطّي",
}
_EXTRA_ORDER = ("nfc", "logo", "qr", "name_print", "gloss", "matte")
_MODE_LABELS = {"badge": "في مكان محدد", "cover": "تغطي الكارت"}
_POS_LABELS = {
    "center": "منتصف",
    "top-right": "أعلى يمين",
    "top-left": "أعلى شمال",
    "bottom-right": "أسفل يمين",
    "bottom-left": "أسفل شمال",
}
_SIZE_LABELS = {"sm": "صغير", "md": "متوسط", "lg": "كبير"}
_KIND_LABELS = {
    "order": "طلب كارت",
    "personal": "شخصي",
    "reader": "قارئ",
    "callback": "مكالمة",
    "quote": "عرض سعر",
}


def _extras_view(raw):
    """Structured extras for the admin inbox (chips + logo layout + plain label)."""
    empty = {"chips": [], "logo_mode": None, "logo_pos": None, "logo_size": None, "label": ""}
    if not raw:
        return empty
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return {**empty, "label": str(raw)}
    if not isinstance(data, dict):
        return {**empty, "label": str(raw)}

    chips = []
    for key in _EXTRA_ORDER:
        if key not in data:
            continue
        chips.append({
            "key": key,
            "label": _EXTRA_LABELS.get(key, key),
            "on": bool(data.get(key)),
        })

    logo_mode = logo_pos = logo_size = None
    if data.get("logo"):
        logo_mode = _MODE_LABELS.get(data.get("logo_mode"), data.get("logo_mode"))
        if data.get("logo_mode") != "cover":
            logo_pos = _POS_LABELS.get(data.get("logo_pos"), data.get("logo_pos"))
            logo_size = _SIZE_LABELS.get(data.get("logo_size"), data.get("logo_size"))

    on_parts = [c["label"] for c in chips if c["on"]]
    if logo_mode:
        on_parts.append("وضع الصورة: " + str(logo_mode))
    if logo_pos:
        on_parts.append("مكان: " + str(logo_pos))
    if logo_size:
        on_parts.append("حجم: " + str(logo_size))

    return {
        "chips": chips,
        "logo_mode": logo_mode,
        "logo_pos": logo_pos,
        "logo_size": logo_size,
        "label": " · ".join(on_parts),
    }


def _extras_label(raw):
    return _extras_view(raw)["label"]


def _wa_link(phone: str | None) -> str | None:
    digits = re.sub(r"\D+", "", phone or "")
    if not digits:
        return None
    if digits.startswith("0") and len(digits) == 11:
        digits = "20" + digits[1:]
    elif len(digits) == 10 and digits.startswith("1"):
        digits = "20" + digits
    return "https://wa.me/" + digits


def _tel_link(phone: str | None) -> str | None:
    digits = re.sub(r"\D+", "", phone or "")
    if not digits:
        return None
    return "tel:" + digits

_VALID_THRU = re.compile(r"^(\d{2})/(\d{2})$")
_PLACEHOLDER = {
    "name": "[MEMBER NAME]",
    "member_no": "0000 0000 0000",
    "valid": "[MM/YY]",
    "tier": "member",
    "accent": "lime",
    "tier_label": "MEMBER",
    "benefits_title": BENEFITS["member"][0],
    "benefits": BENEFITS["member"][1],
    "frozen": False,
}


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            # 404, not 403 — don't even confirm the admin area exists to a non-admin.
            abort(404)
        return view(*args, **kwargs)
    return wrapped


@bp.route("/")
@admin_required
def dashboard():
    members = (
        db.session.query(User, MembershipCard)
        .join(MembershipCard, MembershipCard.user_id == User.id)
        .order_by(User.created_at.asc())
        .all()
    )
    members = list(members)
    selected_pair = members[0] if members else None
    selected = selected_pair[0] if selected_pair else None
    selected_card = selected_pair[1] if selected_pair else None
    views = {user.id: present_card(card, user) for user, card in members}
    presentation = views[selected.id] if selected else _PLACEHOLDER
    return render_template(
        "admin/dashboard.html",
        members=members,
        tiers=TIER_CHOICES,
        tier_meta=TIER_META,
        accents=ACCENTS,
        views=views,
        selected=selected,
        selected_card=selected_card,
        presentation=presentation,
    )


@bp.route("/leads")
@admin_required
def leads():
    kind = (request.args.get("kind") or "all").strip()
    status = (request.args.get("status") or "all").strip()
    allowed_kinds = set(_KIND_LABELS)
    allowed_status = {"new", "contacted", "closed"}

    query = Lead.query
    if kind in allowed_kinds:
        query = query.filter(Lead.kind == kind)
    if status in allowed_status:
        query = query.filter(Lead.status == status)

    rows = query.order_by(Lead.created_at.desc()).limit(200).all()
    for row in rows:
        extras = _extras_view(row.extras)
        row.extras_label = extras["label"]
        row.extras_chips = extras["chips"]
        row.logo_mode_label = extras["logo_mode"]
        row.logo_pos_label = extras["logo_pos"]
        row.logo_size_label = extras["logo_size"]
        row.kind_label = _KIND_LABELS.get(row.kind, row.kind)
        row.wa_url = _wa_link(row.whatsapp or row.phone)
        row.tel_url = _tel_link(row.phone)
        row.print_name = row.name or row.line1

    stats = {
        "all": Lead.query.count(),
        "new": Lead.query.filter_by(status="new").count(),
        "order": Lead.query.filter_by(kind="order").count(),
        "contacted": Lead.query.filter_by(status="contacted").count(),
        "closed": Lead.query.filter_by(status="closed").count(),
    }
    return render_template(
        "admin/leads.html",
        leads=rows,
        stats=stats,
        filter_kind=kind if kind in allowed_kinds else "all",
        filter_status=status if status in allowed_status else "all",
        kind_labels=_KIND_LABELS,
    )


@bp.route("/leads/<int:lead_id>/status", methods=["POST"])
@admin_required
def lead_status(lead_id):
    lead = db.session.get(Lead, lead_id)
    if lead is None:
        abort(404)
    status = request.form.get("status")
    if status not in {"new", "contacted", "closed"}:
        flash("حالة غير صحيحة.", "danger")
        return redirect(url_for("admin.leads"))
    lead.status = status
    db.session.commit()
    log_action("lead_status", detail=f"lead_id={lead_id} status={status}")
    flash("تم تحديث حالة الطلب.", "success")
    next_kind = request.form.get("filter_kind") or "all"
    next_status = request.form.get("filter_status") or "all"
    return redirect(url_for("admin.leads", kind=next_kind, status=next_status))


def _password_classes(password: str) -> int:
    return sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(not c.isalnum() for c in password),
    ])


def _wants_json():
    return request.headers.get("X-Requested-With") == "fetch"


def _parse_valid_thru(raw: str):
    match = _VALID_THRU.match((raw or "").strip())
    if not match:
        return None
    month, year = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        return None
    return date(2000 + year, month, 1)


@bp.route("/member/<int:user_id>/details", methods=["POST"])
@admin_required
def update_details(user_id):
    user = db.session.get(User, user_id)
    if user is None or user.card is None:
        abort(404)

    name = (request.form.get("name") or "").strip()
    member_no = (request.form.get("member_no") or "").strip()
    tier = request.form.get("tier") or ""
    accent = request.form.get("accent") or ""
    valid_until = _parse_valid_thru(request.form.get("valid_thru") or "")

    error = None
    if not 2 <= len(name) <= 120:
        error = "Name must be between 2 and 120 characters."
    elif not member_no or len(member_no) > 32:
        error = "Enter a member number."
    elif tier not in TIER_META:
        error = "Invalid tier."
    elif accent_id(accent_hex(accent)) != accent:
        error = "Invalid accent color."
    elif valid_until is None:
        error = "Valid thru must look like 09/27."
    else:
        taken = MembershipCard.query.filter(
            MembershipCard.member_no == member_no,
            MembershipCard.id != user.card.id,
        ).first()
        if taken:
            error = "That member number is already in use."

    if error:
        if _wants_json():
            return jsonify(ok=False, error=error), 400
        flash(error, "danger")
        return redirect(url_for("admin.dashboard"))

    user.name = name
    user.card.member_no = member_no
    user.card.tier = tier
    user.card.accent_hex = accent_hex(accent)
    user.card.valid_until = valid_until
    db.session.commit()
    log_action("admin_update_card", detail=f"user_id={user_id} tier={tier}")

    if _wants_json():
        return jsonify(ok=True)
    flash(f"Updated {user.name}'s card.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.route("/members", methods=["POST"])
@admin_required
def add_member():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").lower().strip()
    password = request.form.get("password") or ""

    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        flash("Enter a valid email.", "danger")
        return redirect(url_for("admin.dashboard"))

    if not 2 <= len(name) <= 120:
        flash("Name must be between 2 and 120 characters.", "danger")
        return redirect(url_for("admin.dashboard"))
    if User.query.filter_by(email=email).first():
        flash("An account with this email already exists.", "danger")
        return redirect(url_for("admin.dashboard"))

    if len(password) < 10 or _password_classes(password) < 3:
        flash("Use at least 10 characters with a mix of upper/lowercase letters, numbers, and symbols.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    card = MembershipCard(
        user_id=user.id,
        member_no=generate_member_no(),
        tier="member",
        accent_hex=accent_hex("lime"),
        valid_until=date.today() + timedelta(days=365),
    )
    db.session.add(card)
    db.session.commit()
    log_action("admin_add_member", detail=f"user_id={user.id}")
    flash(f"Added {name}.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.route("/member/<int:user_id>/tier", methods=["POST"])
@admin_required
def set_tier(user_id):
    new_tier = request.form.get("tier")
    if new_tier not in TIER_CHOICES:
        flash("Invalid tier.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = db.session.get(User, user_id)
    if user is None or user.card is None:
        abort(404)

    user.card.tier = new_tier
    db.session.commit()
    log_action("admin_set_tier", detail=f"user_id={user_id} tier={new_tier}")
    flash(f"Updated {user.name}'s tier to {new_tier.title()}.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.route("/member/<int:user_id>/freeze", methods=["POST"])
@admin_required
def toggle_freeze(user_id):
    user = db.session.get(User, user_id)
    if user is None or user.card is None:
        abort(404)

    user.card.is_frozen = not user.card.is_frozen
    db.session.commit()
    log_action("admin_toggle_freeze", detail=f"user_id={user_id} frozen={user.card.is_frozen}")
    flash(f"{'Froze' if user.card.is_frozen else 'Unfroze'} {user.name}'s card.", "success")
    return redirect(url_for("admin.dashboard"))
