from pathlib import Path
import json

from flask import Response, current_app, jsonify, redirect, send_from_directory, url_for

from flask_wtf.csrf import generate_csrf

from app.cms import public_payload, seed_cms_if_empty
from app.extensions import limiter
from app.leads import create_lead
from app.main import bp

PAGES = Path(__file__).resolve().parents[1] / "pages"


_MOBILE_HEAD = (
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="theme-color" content="#120b07">\n'
    '<link rel="stylesheet" href="/static/css/site-nav.css">\n'
    '<link rel="stylesheet" href="/static/css/mobile.css?v=1">\n'
)


def _page(name: str):
    seed_cms_if_empty()
    html = (PAGES / name).read_text(encoding="utf-8")
    payload = json.dumps(public_payload(), ensure_ascii=False)
    inject = (
        "<script>window.__CMS__="
        + payload
        + ";</script>\n"
    )
    if 'name="viewport"' not in html:
        if "<head>" in html:
            html = html.replace("<head>", "<head>\n" + _MOBILE_HEAD, 1)
        else:
            html = _MOBILE_HEAD + html
    else:
        head_bits = ""
        if "mobile.css" not in html:
            head_bits += '<link rel="stylesheet" href="/static/css/mobile.css?v=1">\n'
        if "site-nav.css" not in html:
            head_bits += '<link rel="stylesheet" href="/static/css/site-nav.css">\n'
        if head_bits and "</head>" in html:
            html = html.replace("</head>", head_bits + "</head>", 1)
    if "</head>" in html:
        html = html.replace("</head>", inject + "</head>", 1)
    else:
        html = inject + html
    foot_bits = ""
    if "site-nav.js" not in html:
        foot_bits += '<script src="/static/js/site-nav.js"></script>\n'
    if "mobile-scale.js" not in html:
        foot_bits += '<script src="/static/js/mobile-scale.js?v=1"></script>\n'
    if foot_bits:
        if "</body>" in html:
            html = html.replace("</body>", foot_bits + "</body>", 1)
        else:
            html += foot_bits
    return Response(html, mimetype="text/html; charset=utf-8")


@bp.route("/")
def index():
    return _page("home.html")


@bp.route("/personal")
def personal():
    return _page("personal.html")


@bp.route("/readers")
def readers():
    return _page("readers.html")


@bp.route("/flex")
@bp.route("/bends")
def flex():
    return _page("flex.html")


@bp.route("/order")
def order():
    return redirect("/#studio")


@bp.route("/api/csrf")
def csrf_token():
    return jsonify(csrf_token=generate_csrf())


@bp.route("/api/cms")
def cms_api():
    seed_cms_if_empty()
    return jsonify(public_payload())


@bp.route("/api/leads/<kind>", methods=["POST"])
@limiter.limit("8 per minute")
def submit_lead(kind):
    payload, status = create_lead(kind)
    return jsonify(payload), status


@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    folder = Path(current_app.instance_path) / "uploads"
    return send_from_directory(folder, filename)
