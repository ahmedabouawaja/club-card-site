"""Admin CMS — hidden behind admin_required (404 for everyone else)."""
from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user

from sqlalchemy import func

from app.admin import bp
from app.admin.routes import admin_required
from app.cms import KIND_LABELS, DEFAULT_SETTINGS, get_setting, set_setting, items_of, seed_cms_if_empty
from app.extensions import db
from app.models import CmsItem
from app.utils import log_action

KINDS = list(KIND_LABELS.keys())
PAGES = ["home", "personal", "flex", "readers"]


@bp.route("/content")
@admin_required
def content():
    seed_cms_if_empty()
    kind = request.args.get("kind") or "design"
    if kind not in KIND_LABELS:
        kind = "design"
    settings = {k: get_setting(k) for k in DEFAULT_SETTINGS}
    items = items_of(kind, active_only=False)
    return render_template(
        "admin/content.html",
        kind=kind,
        kinds=KIND_LABELS,
        items=items,
        settings=settings,
        pages=PAGES,
    )


@bp.route("/content/settings", methods=["POST"])
@admin_required
def content_settings():
    for key in DEFAULT_SETTINGS:
        set_setting(key, (request.form.get(key) or "").strip())
    db.session.commit()
    log_action("cms_settings", detail=f"admin={current_user.id}")
    flash("تم حفظ إعدادات الموقع.", "success")
    return redirect(url_for("admin.content", kind=request.form.get("return_kind") or "design"))


@bp.route("/content/items", methods=["POST"])
@admin_required
def content_item_create():
    kind = (request.form.get("kind") or "design").strip()
    if kind not in KIND_LABELS:
        flash("نوع غير صحيح.", "danger")
        return redirect(url_for("admin.content"))
    title = (request.form.get("title") or "").strip()
    if not title:
        flash("اكتب عنوان العنصر.", "danger")
        return redirect(url_for("admin.content", kind=kind))
    max_sort = db.session.query(func.max(CmsItem.sort_order)).filter_by(kind=kind).scalar() or 0
    page = (request.form.get("page") or "").strip()[:32] or None
    if not page:
        page = {
            "design": "home",
            "use": "home",
            "hero_chip": "home",
            "order_type": "home",
            "flex_use": "flex",
            "faq": "flex",
            "review": "flex",
            "place": "readers",
        }.get(kind)
    item = CmsItem(
        kind=kind,
        title=title[:160],
        subtitle=(request.form.get("subtitle") or "").strip()[:255] or None,
        body=(request.form.get("body") or "").strip() or None,
        color_a=(request.form.get("color_a") or "").strip()[:32] or None,
        color_b=(request.form.get("color_b") or "").strip()[:32] or None,
        text_color=(request.form.get("text_color") or "").strip()[:32] or None,
        icon=(request.form.get("icon") or "").strip()[:255] or None,
        meta=(request.form.get("meta") or "").strip()[:120] or None,
        page=page,
        sort_order=max_sort + 1,
        is_active=True,
    )
    db.session.add(item)
    db.session.commit()
    log_action("cms_create", detail=f"kind={kind} id={item.id}")
    flash("تمت الإضافة.", "success")
    return redirect(url_for("admin.content", kind=kind))


@bp.route("/content/items/<int:item_id>", methods=["POST"])
@admin_required
def content_item_update(item_id):
    item = db.session.get(CmsItem, item_id)
    if item is None:
        abort(404)
    action = request.form.get("action") or "save"
    kind = item.kind

    if action == "delete":
        db.session.delete(item)
        db.session.commit()
        log_action("cms_delete", detail=f"id={item_id}")
        flash("تم الحذف.", "success")
        return redirect(url_for("admin.content", kind=kind))

    if action == "toggle":
        item.is_active = not item.is_active
        db.session.commit()
        flash("تم تحديث الظهور.", "success")
        return redirect(url_for("admin.content", kind=kind))

    if action == "up":
        _swap_sort(item, -1)
        return redirect(url_for("admin.content", kind=kind))

    if action == "down":
        _swap_sort(item, 1)
        return redirect(url_for("admin.content", kind=kind))

    title = (request.form.get("title") or "").strip()
    if not title:
        flash("العنوان مطلوب.", "danger")
        return redirect(url_for("admin.content", kind=kind))
    item.title = title[:160]
    item.subtitle = (request.form.get("subtitle") or "").strip()[:255] or None
    item.body = (request.form.get("body") or "").strip() or None
    item.color_a = (request.form.get("color_a") or "").strip()[:32] or None
    item.color_b = (request.form.get("color_b") or "").strip()[:32] or None
    item.text_color = (request.form.get("text_color") or "").strip()[:32] or None
    item.icon = (request.form.get("icon") or "").strip()[:255] or None
    item.meta = (request.form.get("meta") or "").strip()[:120] or None
    item.page = (request.form.get("page") or "").strip()[:32] or None
    db.session.commit()
    log_action("cms_update", detail=f"id={item_id}")
    flash("تم الحفظ.", "success")
    return redirect(url_for("admin.content", kind=kind))


def _swap_sort(item: CmsItem, direction: int) -> None:
    siblings = items_of(item.kind, active_only=False)
    idx = next((i for i, x in enumerate(siblings) if x.id == item.id), None)
    if idx is None:
        return
    j = idx + direction
    if j < 0 or j >= len(siblings):
        return
    other = siblings[j]
    item.sort_order, other.sort_order = other.sort_order, item.sort_order
    db.session.commit()
