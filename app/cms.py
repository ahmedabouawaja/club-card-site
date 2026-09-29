"""Public content loaded by the site — editable from the hidden admin CMS."""
from __future__ import annotations

from app.extensions import db
from app.models import CmsItem, SiteSetting

DEFAULT_SETTINGS = {
    "brand_name": "كارد لينك",
    "whatsapp": "20XXXXXXXXXX",
    "hero_kicker": "بطاقات PVC ذكية — للأفراد والشركات",
    "hero_title": "كل التواصل\nفي لمسة واحدة",
    "hero_text": "بطاقات PVC مرنة لا تنكسر، مطبوعة بصورتك وهويتك ومجهزة بـ NFC و QR — بكميات تناسب الأفراد والمحلات والشركات.",
    "flex_title": "كارت فليكس — ينثني في الجيب، ويدخل الباب، ويرجع شكله",
    "flex_lede": "مش كتالوج ألوان وكميات. الكارت ده للجيم، للموظف، للطالب، أو لكارت الولاء في المحل — نفس المقاس البنكي، وNFC وQR لو الموبايل قديم.",
    "flex_price": "من ٨٫٥٠ ج.م",
    "flex_price_note": "سعر القطعة عند طلب جملة للمكان. السعر النهائي حسب العدد والاستخدام.",
    "personal_tagline": "كارت شخصي ذكي — لمسة واحدة تفتح كل روابطك",
    "readers_headline": "ادخل بلمسة.",
    "readers_text": "قارئ البطاقات عند المدخل، ومكان العمل، والنادي، والجيم.",
}

KIND_LABELS = {
    "design": "أشكال الكروت",
    "use": "الاستخدامات",
    "hero_chip": "اختيارات الهيرو",
    "order_type": "أنواع الطلب",
    "flex_use": "استخدامات فليكس",
    "faq": "أسئلة وأجوبة",
    "review": "تقييمات",
    "place": "أماكن القارئات",
}

DEFAULT_ITEMS = [
    ("design", 0, "أبيض خام", "", "", "#ffffff", "#efe8de", "#1f1a16", "", "home", None),
    ("design", 1, "أسود مطفي", "", "", "#2e2a27", "#0f0d0c", "#ffffff", "", "home", None),
    ("design", 2, "ذهبي", "", "", "#f3dc92", "#c99c46", "#3b2a0c", "", "home", None),
    ("design", 3, "أخضر زمردي", "", "", "#138a7e", "#0a4a45", "#eafff9", "", "home", None),
    ("design", 10, "أسود مطفي", "هادي وواثق — اسمك بالأبيض على أسود مطفي.", "", "#2a2c31", "#0c0d0f", "#ffffff", "", "personal", None),
    ("design", 11, "أبيض كلاسيك", "نظيف وبسيط — الشكل الأوضح للاسم والبيانات.", "", "#ffffff", "#e4e7ea", "#1b1f24", "", "personal", None),
    ("design", 12, "ذهبي", "لمعة فخمة تلفت النظر من أول مرة.", "", "#f3dc92", "#c99c46", "#3b2a0c", "", "personal", None),
    ("design", 13, "أخضر زمردي", "لون مختلف وهادي من غير مبالغة.", "", "#138a7e", "#0a4a45", "#eafff9", "", "personal", None),
    ("use", 0, "عضوية الأندية والجيم", "دخول سريع وتجديد الاشتراك", "", None, None, None, "M6 7v10M3 9v6M18 7v10M21 9v6M6 12h12", "home", None),
    ("use", 1, "بطاقات الولاء", "نقاط وخصومات لعملائك الدائمين", "", None, None, None, "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z", "home", None),
    ("use", 2, "هوية الموظفين", "اسم وصورة ورقم لكل موظف", "", None, None, None, "M4 5h16v14H4zM8 10a2 2 0 1 0 4 0 2 2 0 0 0-4 0M6.5 16c.6-1.6 1.9-2.5 3.5-2.5s2.9.9 3.5 2.5M15 9h3M15 12h3", "home", None),
    ("use", 3, "المدارس والجامعات", "بطاقة طالب وحضور بالـ QR", "", None, None, None, "M2 9l10-5 10 5-10 5zM6 11v5c3 2.5 9 2.5 12 0v-5", "home", None),
    ("use", 4, "كارت شخصي ذكي", "لمسة NFC تفتح كل روابطك", "", None, None, None, "M8 8a6 6 0 0 1 0 8M11.5 5.5a10 10 0 0 1 0 13M15 3a14 14 0 0 1 0 18", "home", None),
    ("use", 5, "دخول المباني والفنادق", "بطاقات دخول ذكية", "", None, None, None, "M7.5 14a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7zM11 10.5h10M17 10.5v3M20 10.5v2", "home", None),
    ("hero_chip", 0, "للجيم والنادي", "عضوية الجيم والنادي", "كارت يدخل الباب ويعيش في الجيب. اختار الشكل اللي يناسب النادي.", None, None, None, "2", "home", "0"),
    ("hero_chip", 1, "هوية موظفين", "هوية ودخول الموظفين", "اسم وصورة ودخول المبنى على نفس الكارت. اختار الشكل الرسمي.", None, None, None, "1", "home", "1"),
    ("hero_chip", 2, "كارت شخصي", "كارتك الشخصي", "باسمك وروابطك. ابدأ بالأبيض أو لون جاهز، وبعدين حط صورتك.", None, None, None, "0", "home", "0"),
    ("order_type", 0, "جيم ونادي", "العضو يمرّر الكارت عند الباب بدل الكشف الورق", "من 50|250 فأكثر", None, None, None, "M6 7v10M3 9v6M18 7v10M21 9v6M6 12h12", "home", None),
    ("order_type", 1, "شركة ومدرسة", "هوية ودخول للموظف أو الطالب على نفس الكارت", "من 50|250 فأكثر", None, None, None, "M4 21V3h11v18M15 8h5v13M8 7h3M8 11h3M8 15h3M3 21h18", "home", None),
    ("flex_use", 0, "جيم أو نادي", "العضو يمرّر الكارت عند الباب بدل الكشف الورق.", "", None, None, None, "", "flex", None),
    ("flex_use", 1, "هوية موظفين", "اسم وصورة ودخول المبنى في كارت واحد.", "", None, None, None, "", "flex", None),
    ("flex_use", 2, "مدرسة أو مركز", "حضور الطالب بالمسح، والكارت يتحمّل الشنطة.", "", None, None, None, "", "flex", None),
    ("flex_use", 3, "ولاء محل", "نفس الكارت للنقاط أو الخصم، لمسة أو QR.", "", None, None, None, "", "flex", None),
    ("faq", 0, "ينفع لجيم فيه حركة كل يوم؟", "", "ده الاستخدام الأساسي. الكارت يدخل الجيب ويروح الباب ويرجع.", None, None, None, "", "flex", None),
    ("faq", 1, "عايز واحدة بس ليا؟", "", "نعم من صفحة الأفراد. الصفحة دي للجملة حسب استخدام المكان.", None, None, None, "", "flex", None),
    ("faq", 2, "لو الشريحة وقفت؟", "", "الـ QR على نفس الكارت يفتح نفس الصفحة. نقدر نوقف الرابط لو الكارت ضاع.", None, None, None, "", "flex", None),
    ("review", 0, "جيم — دمنهور", "بعد شهور على الباب", "الكروت القديمة كانت بتكسر عند الاستقبال. دي داخلة الجيب وطلعة، والقارئ لسه بيقرا.", None, None, None, "", "flex", None),
    ("review", 1, "مركز تعليمي — كفر الدوار", "مع الشنط والكتب", "العيال بيطووا الكارت. فضل راجع شكله، والحضور بالمسح ماشي.", None, None, None, "", "flex", None),
    ("place", 0, "مداخل الشركات والمباني", "الموظف أو الزائر يمرّر البطاقة على القارئ عند الباب.", "", None, None, None, "M6 21V3h12v18M3 21h18M14.5 12v.01", "readers", "مدخل شركة"),
    ("place", 1, "الحضور والانصراف", "تسجيل حضور الموظفين بلمسة بدل الكشوف الورق.", "", None, None, None, "M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z", "readers", "مكان عمل"),
    ("place", 2, "الأندية", "دخول الأعضاء للنادي والمرافق ببطاقة العضوية.", "", None, None, None, "M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0zM7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4", "readers", "نادي"),
    ("place", 3, "الجيم والعضويات", "بطاقة لكل مشترك تُمرَّر عند الدخول لمتابعة الحضور.", "", None, None, None, "M6 7v10M3 9v6M18 7v10M21 9v6M6 12h12", "readers", "جيم"),
]


def get_setting(key: str, default: str = "") -> str:
    row = db.session.get(SiteSetting, key)
    if row and row.value is not None and row.value != "":
        return row.value
    return DEFAULT_SETTINGS.get(key, default)


def set_setting(key: str, value: str) -> None:
    row = db.session.get(SiteSetting, key)
    if row is None:
        row = SiteSetting(key=key, value=value or "")
        db.session.add(row)
    else:
        row.value = value or ""


def items_of(kind: str, page: str | None = None, active_only: bool = True) -> list[CmsItem]:
    q = CmsItem.query.filter_by(kind=kind)
    if page:
        q = q.filter_by(page=page)
    if active_only:
        q = q.filter_by(is_active=True)
    return q.order_by(CmsItem.sort_order.asc(), CmsItem.id.asc()).all()


def seed_cms_if_empty() -> None:
    if SiteSetting.query.count() == 0:
        for key, value in DEFAULT_SETTINGS.items():
            db.session.add(SiteSetting(key=key, value=value))
    if CmsItem.query.count() == 0:
        for kind, sort, title, subtitle, body, ca, cb, tc, icon, page, meta in DEFAULT_ITEMS:
            db.session.add(CmsItem(
                kind=kind,
                sort_order=sort,
                title=title,
                subtitle=subtitle or None,
                body=body or None,
                color_a=ca,
                color_b=cb,
                text_color=tc,
                icon=icon or None,
                page=page,
                meta=meta,
                is_active=True,
            ))
    db.session.commit()


def _grad(a: str | None, b: str | None) -> str:
    a = a or "#ffffff"
    b = b or a
    return f"linear-gradient(135deg, {a}, {b})"


def public_payload() -> dict:
    settings = {k: get_setting(k) for k in DEFAULT_SETTINGS}
    home_designs = items_of("design", "home")
    personal_designs = items_of("design", "personal")
    uses = items_of("use", "home")
    chips = items_of("hero_chip", "home")
    order_types = items_of("order_type", "home")
    flex_uses = items_of("flex_use", "flex")
    faqs = items_of("faq", "flex")
    reviews = items_of("review", "flex")
    places = items_of("place", "readers")

    return {
        "settings": settings,
        "homeDesigns": [
            {
                "name": i.title,
                "short": i.title,
                "swatch": _grad(i.color_a, i.color_b),
                "fg": i.text_color or "#1f1a16",
                "a": i.color_a,
                "b": i.color_b,
            }
            for i in home_designs
        ],
        "personalDesigns": [
            {
                "name": i.title,
                "desc": i.subtitle or "",
                "bg": _grad(i.color_a, i.color_b),
                "fg": i.text_color or "#ffffff",
                "sub": "rgba(255,255,255,0.62)" if (i.text_color or "").lower() in {"#ffffff", "#eafff9"} else "rgba(27,31,36,0.62)",
                "shine": "rgba(255,255,255,0.2)",
            }
            for i in personal_designs
        ],
        "uses": [
            {"t": i.title, "d": i.subtitle or "", "icon": i.icon or "M12 3v18"}
            for i in uses
        ],
        "heroChips": [
            {
                "label": i.title,
                "hint": i.subtitle or i.title,
                "blurb": i.body or "",
                "tpl": int(i.icon or "0") if (i.icon or "").isdigit() else 0,
                "type": int(i.meta or "0") if (i.meta or "").isdigit() else 0,
            }
            for i in chips
        ],
        "orderTypes": [
            {
                "name": i.title,
                "desc": i.subtitle or "",
                "qtys": [x for x in (i.body or "من 50|250 فأكثر").split("|") if x],
                "icon": i.icon or "M12 3v18",
            }
            for i in order_types
        ],
        "flexUses": [
            {"title": i.title, "body": i.subtitle or i.body or ""}
            for i in flex_uses
        ],
        "faqs": [
            {"q": i.title, "a": i.body or ""}
            for i in faqs
        ],
        "reviews": [
            {"title": i.title, "sub": i.subtitle or "", "body": i.body or ""}
            for i in reviews
        ],
        "places": [
            {
                "t": i.title,
                "d": i.subtitle or i.body or "",
                "icon": i.icon or "M12 3v18",
                "chip": i.meta or i.title,
            }
            for i in places
        ],
    }
