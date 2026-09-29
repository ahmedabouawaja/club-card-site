"""Visual system for the membership card, shared by the public card and admin studio."""

ACCENTS = [
    {"id": "lime", "hex": "#D6FF3E"},
    {"id": "orange", "hex": "#FF4D1C"},
    {"id": "cyan", "hex": "#2DE2D0"},
    {"id": "gold", "hex": "#E2B340"},
    {"id": "silver", "hex": "#D5D8DE"},
]

_ACCENT_BY_ID = {item["id"]: item["hex"] for item in ACCENTS}
_ACCENT_BY_HEX = {item["hex"].lower(): item["id"] for item in ACCENTS}

TIER_META = {
    "member": {"label": "Member", "pill": "MEMBER"},
    "silver": {"label": "Silver", "pill": "SILVER MEMBER"},
    "gold": {"label": "Gold", "pill": "GOLD MEMBER"},
    "black": {"label": "Black", "pill": "BLACK MEMBER"},
}

BENEFITS = {
    "member": (
        "MEMBER BENEFITS",
        ["Unlimited gym access", "Group classes & coaching", "[PARTNER DISCOUNTS]"],
    ),
    "silver": (
        "SILVER BENEFITS",
        ["All Member benefits", "Priority class booking", "Locker included"],
    ),
    "gold": (
        "GOLD BENEFITS",
        ["All Silver benefits", "Unlimited PT booking", "1 guest pass / month"],
    ),
    "black": (
        "BLACK BENEFITS",
        ["All Gold benefits", "Private suite access", "Concierge booking"],
    ),
}

DEFAULT_ACCENT = {
    "member": "lime",
    "silver": "silver",
    "gold": "gold",
    "black": "lime",
}


def accent_id(hex_value: str | None) -> str:
    if not hex_value:
        return "lime"
    return _ACCENT_BY_HEX.get(hex_value.strip().lower(), "lime")


def accent_hex(accent: str) -> str:
    return _ACCENT_BY_ID.get(accent, _ACCENT_BY_ID["lime"])


def present_card(card, user) -> dict:
    tier = card.tier if card.tier in TIER_META else "member"
    title, items = BENEFITS[tier]
    pill = TIER_META[tier]["pill"]
    if card.is_frozen:
        pill = f"{pill} · FROZEN"
    return {
        "name": user.name,
        "member_no": card.member_no,
        "valid": card.valid_until.strftime("%m/%y"),
        "tier": tier,
        "accent": accent_id(card.accent_hex),
        "tier_label": pill,
        "benefits_title": title,
        "benefits": items,
        "frozen": card.is_frozen,
    }
