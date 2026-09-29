"""Turn the unpacked design pages into Flask-served HTML + static assets."""
import gzip
import json
import re
import shutil
from base64 import b64decode
from pathlib import Path

ROOT = Path(r"A:\New folder\club_card_site")
SRC = ROOT / "_unpacked"
STATIC = ROOT / "app" / "static" / "dc"
PAGES = ROOT / "app" / "pages"
STATIC.mkdir(parents=True, exist_ok=True)
PAGES.mkdir(parents=True, exist_ok=True)

MAP = {
    "00_c879051a": ("home.html", "/"),
    "01_6105947d": ("personal.html", "/personal"),
    "02_e5b3c67d": ("readers.html", "/readers"),
}

LINKS = {
    "Scanner.dc.html": "/readers",
    "Personal.dc.html": "/personal",
    "Main.dc.html": "/",
}

def unpack_manifest(html_path: Path, dest_dir: Path) -> dict[str, str]:
    text = html_path.read_text(encoding="utf-8")
    match = re.search(r'<script type="__bundler/manifest">\s*(.*?)\s*</script>', text, re.S)
    manifest = json.loads(match.group(1))
    dest_dir.mkdir(parents=True, exist_ok=True)
    url_map = {}
    for uuid, meta in manifest.items():
        raw = b64decode(meta["data"])
        if meta.get("compressed"):
            raw = gzip.decompress(raw)
        mime = meta.get("mime", "")
        ext = ".js" if "javascript" in mime else ".woff2" if "font" in mime or "woff" in mime else ".bin"
        name = uuid + ext
        (dest_dir / name).write_bytes(raw)
        url_map[uuid] = f"/static/dc/{dest_dir.name}/{name}"
    return url_map


def rewrite(html: str, url_map: dict[str, str], dest_dir: Path) -> str:
    for uuid, url in url_map.items():
        html = html.replace(uuid, url)
    for old, new in LINKS.items():
        html = html.replace(old, new)
    js_files = sorted(dest_dir.glob("*.js"), key=lambda p: p.stat().st_size)
    # smallest = React, middle = dc-runtime, largest = ReactDOM
    # Want: React, ReactDOM, dc-runtime
    by_size = list(js_files)
    react, runtime, react_dom = by_size[0], by_size[1], by_size[2]
    tags = "\n".join(
        f'<script src="/static/dc/{dest_dir.name}/{p.name}"></script>'
        for p in (react, react_dom, runtime)
    )
    html = re.sub(r"<script src=\"[^\"]+\"></script>", tags, html, count=1)
    extra = '<script src="/static/js/leads.js"></script>\n</body>'
    if "</body>" in html:
        html = html.replace("</body>", extra, 1)
    return html


for folder, (page_name, _) in MAP.items():
    src_html = SRC / f"{folder}.html"
    dest = STATIC / folder
    if dest.exists():
        shutil.rmtree(dest)
    urls = unpack_manifest(src_html, dest)
    template = (SRC / "inner" / folder / "template.html").read_text(encoding="utf-8")
    (PAGES / page_name).write_text(rewrite(template, urls, dest), encoding="utf-8")
    print(page_name, "assets", len(urls))
