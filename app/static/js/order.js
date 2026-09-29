(function () {
  const state = {
    hue: 24,
    sat: 0.72,
    light: 0.42,
    hex: "#8A4B1F",
    logoFile: null,
    logoUrl: null,
    logoMode: "badge",
    logoPos: "center",
    logoSize: "md",
  };

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const card = $("[data-card]");
  const wheel = $("[data-wheel]");
  const knob = $("[data-wheel-knob]");
  const shade = $("[data-shade]");
  const swatch = $("[data-swatch]");
  const hexInput = $("[data-hex]");
  const nfcMark = $("[data-nfc-mark]");
  const qrMark = $("[data-qr-mark]");
  const chip = $("[data-chip]");
  const logoWrap = $("[data-logo-wrap]");
  const logoImg = $("[data-logo-img]");
  const fullWrap = $("[data-fullimg]");
  const fullImg = $("[data-fullimg-src]");
  const logoBox = $("[data-logo-box]");
  const logoFile = $("[data-logo-file]");
  const logoName = $("[data-logo-name]");
  const placeControls = $("[data-place-controls]");
  const cardName = $("[data-card-name]");
  const printName = $("[data-print-name]");
  const errEl = $("[data-error]");
  let csrf = "";

  function hslToHex(h, s, l) {
    s = Math.max(0, Math.min(1, s));
    l = Math.max(0, Math.min(1, l));
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;
    let r = 0, g = 0, b = 0;
    if (h < 60) [r, g, b] = [c, x, 0];
    else if (h < 120) [r, g, b] = [x, c, 0];
    else if (h < 180) [r, g, b] = [0, c, x];
    else if (h < 240) [r, g, b] = [0, x, c];
    else if (h < 300) [r, g, b] = [x, 0, c];
    else [r, g, b] = [c, 0, x];
    const to = (v) => Math.round((v + m) * 255).toString(16).padStart(2, "0");
    return ("#" + to(r) + to(g) + to(b)).toUpperCase();
  }

  function hexToHsl(hex) {
    const m = /^#?([0-9a-f]{6})$/i.exec(hex || "");
    if (!m) return null;
    let r = parseInt(m[1].slice(0, 2), 16) / 255;
    let g = parseInt(m[1].slice(2, 4), 16) / 255;
    let b = parseInt(m[1].slice(4, 6), 16) / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0;
    const l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)); break;
        case g: h = ((b - r) / d + 2); break;
        default: h = ((r - g) / d + 4); break;
      }
      h *= 60;
    }
    return { h, s, l };
  }

  function inkFor(hex) {
    const m = /^#?([0-9a-f]{6})$/i.exec(hex);
    if (!m) return "#fff6e6";
    const r = parseInt(m[1].slice(0, 2), 16);
    const g = parseInt(m[1].slice(2, 4), 16);
    const b = parseInt(m[1].slice(4, 6), 16);
    const y = (r * 299 + g * 587 + b * 114) / 1000;
    return y > 150 ? "#1a1008" : "#fff6e6";
  }

  function drawWheel() {
    if (!wheel) return;
    const ctx = wheel.getContext("2d");
    const size = wheel.width;
    const cx = size / 2;
    const cy = size / 2;
    const outer = size / 2 - 2;
    const inner = outer * 0.55;
    ctx.clearRect(0, 0, size, size);
    for (let a = 0; a < 360; a++) {
      const rad0 = ((a - 90) * Math.PI) / 180;
      const rad1 = ((a + 1 - 90) * Math.PI) / 180;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(rad0) * inner, cy + Math.sin(rad0) * inner);
      ctx.arc(cx, cy, outer, rad0, rad1);
      ctx.lineTo(cx + Math.cos(rad1) * inner, cy + Math.sin(rad1) * inner);
      ctx.arc(cx, cy, inner, rad1, rad0, true);
      ctx.closePath();
      ctx.fillStyle = "hsl(" + a + " 100% 50%)";
      ctx.fill();
    }
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, inner - 2);
    g.addColorStop(0, hslToHex(state.hue, 0.15, state.light));
    g.addColorStop(1, hslToHex(state.hue, state.sat, state.light));
    ctx.beginPath();
    ctx.arc(cx, cy, inner - 2, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
  }

  function placeKnob() {
    if (!knob) return;
    const size = 220;
    const cx = size / 2;
    const cy = size / 2;
    const r = size / 2 * 0.78;
    const rad = ((state.hue - 90) * Math.PI) / 180;
    knob.style.left = cx + Math.cos(rad) * r + "px";
    knob.style.top = cy + Math.sin(rad) * r + "px";
    knob.style.background = state.hex;
  }

  function applyColor() {
    state.hex = hslToHex(state.hue, state.sat, state.light);
    document.documentElement.style.setProperty("--card-color", state.hex);
    document.documentElement.style.setProperty("--card-ink", inkFor(state.hex));
    if (swatch) swatch.style.background = state.hex;
    if (hexInput && document.activeElement !== hexInput) hexInput.value = state.hex;
    drawWheel();
    placeKnob();
  }

  function pickFromEvent(e) {
    const rect = wheel.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    const dist = Math.sqrt(x * x + y * y);
    if (dist < 0.28 || dist > 0.5) return;
    let deg = (Math.atan2(y, x) * 180) / Math.PI + 90;
    if (deg < 0) deg += 360;
    state.hue = deg;
    state.sat = 0.85;
    applyColor();
  }

  function readLogoLayout() {
    const modeEl = document.querySelector("[data-logo-mode]:checked");
    const posEl = $("[data-logo-pos]");
    const sizeEl = $("[data-logo-size]");
    state.logoMode = modeEl ? modeEl.value : "badge";
    state.logoPos = posEl ? posEl.value : "center";
    state.logoSize = sizeEl ? sizeEl.value : "md";
  }

  function applyLogoLayout() {
    readLogoLayout();
    if (!card) return;
    card.dataset.logoMode = state.logoMode;
    card.dataset.logoPos = state.logoPos;
    card.dataset.logoSize = state.logoSize;
    card.classList.toggle("is-cover-mode", state.logoMode === "cover" && !!state.logoUrl);

    const hasLogo = !!state.logoUrl;
    const isCover = state.logoMode === "cover" && hasLogo;
    const isBadge = state.logoMode === "badge" && hasLogo;

    if (fullWrap) fullWrap.hidden = !isCover;
    if (logoWrap) logoWrap.hidden = !isBadge;
    if (placeControls) placeControls.hidden = state.logoMode === "cover";
    if (chip) chip.style.opacity = isCover ? "0.55" : "1";
  }

  function syncExtras() {
    const on = (name) => {
      const el = document.querySelector('[data-extra][name="' + name + '"]');
      return el && el.checked;
    };
    if (nfcMark) nfcMark.hidden = !on("nfc");
    if (qrMark) qrMark.hidden = !on("qr");
    if (logoBox) logoBox.hidden = !on("logo");

    if (on("logo")) applyLogoLayout();
    else {
      if (logoWrap) logoWrap.hidden = true;
      if (fullWrap) fullWrap.hidden = true;
      if (card) card.classList.remove("is-cover-mode");
    }

    if (cardName) {
      const show = on("name_print");
      cardName.hidden = !show;
      if (show && printName && printName.value.trim()) {
        cardName.textContent = printName.value.trim();
      } else if (show) {
        cardName.textContent = "اسمك / شركتك";
      }
    }
    if (card) {
      card.style.filter = on("matte") ? "saturate(.92) contrast(.96)" : "none";
      card.classList.toggle("is-gloss", on("gloss"));
    }
  }

  function goStep(step) {
    $$(".ord-panel").forEach((p) => {
      const id = p.getAttribute("data-step");
      const show = id === String(step);
      p.classList.toggle("is-on", show);
      p.hidden = !show;
    });
    $$("[data-step-dot]").forEach((dot) => {
      const n = Number(dot.getAttribute("data-step-dot"));
      dot.classList.toggle("is-on", String(step) !== "done" && n === Number(step));
      dot.classList.toggle("is-done", String(step) === "done" || (typeof step === "number" && n < step));
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function extrasPayload() {
    const out = {};
    $$("[data-extra]").forEach((el) => { out[el.name] = !!el.checked; });
    if (out.logo) {
      readLogoLayout();
      out.logo_mode = state.logoMode;
      out.logo_pos = state.logoPos;
      out.logo_size = state.logoSize;
    }
    return out;
  }

  function quantityValue() {
    const custom = ($("[data-qty-custom]") || {}).value;
    if (custom && custom.trim()) return custom.trim();
    const picked = document.querySelector("[data-qty]:checked");
    return picked ? picked.value : "";
  }

  function showError(msg) {
    if (!errEl) return;
    errEl.hidden = !msg;
    errEl.textContent = msg || "";
  }

  if (wheel) {
    drawWheel();
    placeKnob();
    applyColor();
    let dragging = false;
    const start = (e) => { dragging = true; pickFromEvent(e); e.preventDefault(); };
    const move = (e) => { if (dragging) pickFromEvent(e); };
    const end = () => { dragging = false; };
    wheel.addEventListener("pointerdown", start);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", end);
  }

  if (shade) {
    shade.addEventListener("input", () => {
      state.light = Number(shade.value) / 100;
      applyColor();
    });
  }

  if (hexInput) {
    hexInput.addEventListener("change", () => {
      let v = hexInput.value.trim();
      if (v && v[0] !== "#") v = "#" + v;
      const hsl = hexToHsl(v);
      if (!hsl) return;
      state.hue = hsl.h;
      state.sat = Math.max(0.35, hsl.s);
      state.light = hsl.l;
      if (shade) shade.value = String(Math.round(hsl.l * 100));
      applyColor();
    });
  }

  $$("[data-extra]").forEach((el) => el.addEventListener("change", syncExtras));
  if (printName) printName.addEventListener("input", syncExtras);
  $$("[data-logo-mode]").forEach((el) => el.addEventListener("change", syncExtras));
  $("[data-logo-pos]")?.addEventListener("change", syncExtras);
  $("[data-logo-size]")?.addEventListener("change", syncExtras);

  if (logoFile) {
    logoFile.addEventListener("change", () => {
      const file = logoFile.files && logoFile.files[0];
      if (state.logoUrl) URL.revokeObjectURL(state.logoUrl);
      state.logoFile = file || null;
      state.logoUrl = file ? URL.createObjectURL(file) : null;
      if (logoImg) logoImg.src = state.logoUrl || "";
      if (fullImg) fullImg.src = state.logoUrl || "";
      if (logoName) logoName.textContent = file ? file.name : "PNG شفاف أفضل — حد 2 ميجا";
      const logoToggle = document.querySelector('[data-extra][name="logo"]');
      if (file && logoToggle && !logoToggle.checked) logoToggle.checked = true;
      syncExtras();
    });
  }

  $("[data-next]")?.addEventListener("click", () => goStep(2));
  $("[data-back]")?.addEventListener("click", () => goStep(1));

  fetch("/api/csrf", { credentials: "same-origin" })
    .then((r) => r.json())
    .then((d) => { csrf = d.csrf_token || ""; })
    .catch(() => {});

  $("[data-order-form]")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError("");
    const phone = ($("[data-phone]") || {}).value || "";
    const whatsapp = ($("[data-whatsapp]") || {}).value || "";
    const address = ($("[data-address]") || {}).value || "";
    const notes = ($("[data-notes]") || {}).value || "";
    const quantity = quantityValue();
    const btn = $("[data-submit]");

    if (!quantity) { showError("حدد الكمية المطلوبة."); return; }
    if (!phone.trim()) { showError("أدخل رقم الموبايل."); return; }
    if (!whatsapp.trim()) { showError("أدخل رقم واتساب."); return; }
    if (address.trim().length < 5) { showError("اكتب العنوان بالتفصيل."); return; }

    const extras = extrasPayload();
    const fd = new FormData();
    fd.append("phone", phone.trim());
    fd.append("whatsapp", whatsapp.trim());
    fd.append("address", address.trim());
    fd.append("quantity", quantity);
    fd.append("color", state.hex);
    fd.append("name", (printName && printName.value.trim()) || "");
    fd.append("line1", (printName && printName.value.trim()) || "");
    fd.append("notes", notes.trim());
    fd.append("extras", JSON.stringify(extras));
    if (state.logoFile) fd.append("image", state.logoFile);

    if (btn) btn.disabled = true;
    try {
      const res = await fetch("/api/leads/order", {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrf },
        body: fd,
      });
      const data = await res.json().catch(() => ({ ok: false }));
      if (!res.ok || !data.ok) {
        showError((data && data.error) || "حصل خطأ، جرّب تاني.");
        if (btn) btn.disabled = false;
        return;
      }
      goStep("done");
    } catch (_) {
      showError("مشكلة في الاتصال. تأكد من النت وجرّب تاني.");
      if (btn) btn.disabled = false;
    }
  });

  const params = new URLSearchParams(location.search);
  const useHint = params.get("use");
  if (useHint && $("[data-notes]")) {
    $("[data-notes]").value = "الاستخدام: " + useHint;
  }

  syncExtras();
})();
