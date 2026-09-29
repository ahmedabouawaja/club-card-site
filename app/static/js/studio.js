/**
 * Static studio (outside React/DC) — direct bindings, no DOM fighting.
 */
(function () {
  const root = document.querySelector("[data-studio]");
  if (!root) return;

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
    rotY: -16,
    rotX: 12,
    rotZ: -5,
    nfc: true,
    logo: false,
    qr: false,
    name_print: true,
    gloss: false,
    matte: false,
    printName: "",
  };

  let csrf = "";
  let dragCard = false;
  let dragWheel = false;
  let lastX = 0;
  let lastY = 0;

  const $ = (sel, el) => (el || document).querySelector(sel);
  const card = () => $("[data-hero-card]") || $("[data-card-shell] .card-live");
  const shell = () => $("[data-card-shell]");

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
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        default: h = (r - g) / d + 4; break;
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
    return (r * 299 + g * 587 + b * 114) / 1000 > 150 ? "#1a1008" : "#fff6e6";
  }

  function drawWheel() {
    const wheel = root.querySelector("[data-wheel]");
    if (!wheel) return;
    wheel.width = 220;
    wheel.height = 220;
    const ctx = wheel.getContext("2d");
    const cx = 110, cy = 110, outer = 108, inner = outer * 0.55;
    ctx.clearRect(0, 0, 220, 220);
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

    const knob = root.querySelector("[data-wheel-knob]");
    if (knob) {
      const rect = wheel.getBoundingClientRect();
      const disp = rect.width || 160;
      const r = disp * 0.39;
      const rad = ((state.hue - 90) * Math.PI) / 180;
      knob.style.left = disp / 2 + Math.cos(rad) * r + "px";
      knob.style.top = disp / 2 + Math.sin(rad) * r + "px";
      knob.style.background = state.hex;
    }
  }

  function paint() {
    state.hex = hslToHex(state.hue, state.sat, state.light);
    document.documentElement.style.setProperty("--card-color", state.hex);
    document.documentElement.style.setProperty("--card-ink", inkFor(state.hex));

    const c = card();
    if (c) {
      c.style.background =
        "linear-gradient(145deg, color-mix(in srgb, " + state.hex + " 88%, #fff), " +
        state.hex + " 45%, color-mix(in srgb, " + state.hex + " 70%, #000))";
      c.style.color = inkFor(state.hex);
      c.style.transform =
        "perspective(1100px) rotateY(" + state.rotY + "deg) rotateX(" +
        state.rotX + "deg) rotateZ(" + state.rotZ + "deg)";
      c.dataset.logoMode = state.logoMode;
      c.dataset.logoPos = state.logoPos;
      c.dataset.logoSize = state.logoSize;
      c.classList.toggle("is-cover-mode", state.logoMode === "cover" && !!state.logoUrl);
      c.style.filter = state.matte ? "saturate(.92) contrast(.96)" : "none";
    }

    const swatch = root.querySelector("[data-swatch]");
    if (swatch) swatch.style.background = state.hex;
    const hexInput = root.querySelector("[data-hex]");
    if (hexInput && document.activeElement !== hexInput) hexInput.value = state.hex;

    const nfc = $("[data-nfc-mark]");
    const qr = $("[data-qr-mark]");
    const chip = $("[data-chip]");
    const logoWrap = $("[data-logo-wrap]");
    const fullWrap = $("[data-fullimg]");
    const logoBox = root.querySelector("[data-logo-box]");
    const place = root.querySelector("[data-place-controls]");
    const cardName = $("[data-card-name]");
    const logoImg = $("[data-logo-img]");
    const fullImg = $("[data-fullimg-src]");

    if (nfc) nfc.hidden = !state.nfc;
    if (qr) qr.hidden = !state.qr;
    if (logoBox) logoBox.hidden = !state.logo;
    if (place) place.hidden = !state.logo || state.logoMode === "cover";

    const hasLogo = state.logo && !!state.logoUrl;
    if (fullWrap) fullWrap.hidden = !(hasLogo && state.logoMode === "cover");
    if (logoWrap) logoWrap.hidden = !(hasLogo && state.logoMode === "badge");
    if (chip) chip.style.opacity = hasLogo && state.logoMode === "cover" ? "0.55" : "1";
    if (logoImg && state.logoUrl) logoImg.src = state.logoUrl;
    if (fullImg && state.logoUrl) fullImg.src = state.logoUrl;
    if (cardName) {
      cardName.hidden = !state.name_print;
      cardName.textContent = state.printName.trim() || "اسمك / شركتك";
    }
    drawWheel();
  }

  function pickWheel(e) {
    const wheel = root.querySelector("[data-wheel]");
    if (!wheel) return;
    const rect = wheel.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    const dist = Math.sqrt(x * x + y * y);
    if (dist < 0.22 || dist > 0.52) return;
    let deg = (Math.atan2(y, x) * 180) / Math.PI + 90;
    if (deg < 0) deg += 360;
    state.hue = deg;
    state.sat = 0.85;
    paint();
  }

  // Direct listeners on stable nodes (outside React)
  root.querySelectorAll("[data-extra]").forEach((el) => {
    el.addEventListener("change", () => {
      state[el.name] = !!el.checked;
      paint();
    });
  });
  root.querySelectorAll("[data-logo-mode]").forEach((el) => {
    el.addEventListener("change", () => {
      if (!el.checked) return;
      state.logoMode = el.value;
      paint();
    });
  });
  root.querySelector("[data-logo-pos]")?.addEventListener("change", (e) => {
    state.logoPos = e.target.value;
    paint();
  });
  root.querySelector("[data-logo-size]")?.addEventListener("change", (e) => {
    state.logoSize = e.target.value;
    paint();
  });
  root.querySelector("[data-shade]")?.addEventListener("input", (e) => {
    state.light = Number(e.target.value) / 100;
    paint();
  });
  root.querySelector("[data-hex]")?.addEventListener("change", (e) => {
    let v = e.target.value.trim();
    if (v && v[0] !== "#") v = "#" + v;
    const hsl = hexToHsl(v);
    if (!hsl) return;
    state.hue = hsl.h;
    state.sat = Math.max(0.35, hsl.s);
    state.light = hsl.l;
    const shade = root.querySelector("[data-shade]");
    if (shade) shade.value = String(Math.round(state.light * 100));
    paint();
  });
  root.querySelector("[data-print-name]")?.addEventListener("input", (e) => {
    state.printName = e.target.value || "";
    paint();
  });
  root.querySelector("[data-logo-file]")?.addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (state.logoUrl) URL.revokeObjectURL(state.logoUrl);
    state.logoFile = file || null;
    state.logoUrl = file ? URL.createObjectURL(file) : null;
    if (file) {
      state.logo = true;
      const toggle = root.querySelector('[data-extra][name="logo"]');
      if (toggle) toggle.checked = true;
    }
    const name = root.querySelector("[data-logo-name]");
    if (name) name.textContent = file ? file.name : "PNG أو JPG";
    paint();
  });

  const wheel = root.querySelector("[data-wheel]");
  if (wheel) {
    wheel.addEventListener("pointerdown", (e) => {
      dragWheel = true;
      pickWheel(e);
      e.preventDefault();
    });
  }
  window.addEventListener("pointermove", (e) => {
    if (dragWheel) pickWheel(e);
    if (!dragCard) return;
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
    state.rotY = Math.max(-55, Math.min(55, state.rotY + dx * 0.4));
    state.rotX = Math.max(-30, Math.min(35, state.rotX - dy * 0.35));
    const c = card();
    if (c) {
      c.style.transform =
        "perspective(1100px) rotateY(" + state.rotY + "deg) rotateX(" +
        state.rotX + "deg) rotateZ(" + state.rotZ + "deg)";
    }
  });
  window.addEventListener("pointerup", () => {
    dragWheel = false;
    dragCard = false;
    shell()?.classList.remove("is-dragging");
  });

  shell()?.addEventListener("pointerdown", (e) => {
    dragCard = true;
    lastX = e.clientX;
    lastY = e.clientY;
    shell().classList.add("is-dragging");
    try { shell().setPointerCapture(e.pointerId); } catch (_) {}
    e.preventDefault();
  });

  root.querySelector("[data-to-order]")?.addEventListener("click", () => {
    document.getElementById("order")?.scrollIntoView({ behavior: "smooth" });
  });

  // Order form (also outside DC)
  const form = document.querySelector("[data-order-form]");
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errEl = $("[data-error]");
    const showErr = (m) => {
      if (!errEl) return;
      errEl.hidden = !m;
      errEl.textContent = m || "";
    };
    showErr("");
    const phone = ($("[data-phone]") || {}).value || "";
    const whatsapp = ($("[data-whatsapp]") || {}).value || "";
    const address = ($("[data-address]") || {}).value || "";
    const notes = ($("[data-notes]") || {}).value || "";
    const custom = ($("[data-qty-custom]") || {}).value;
    const picked = document.querySelector("[data-qty]:checked");
    const quantity = (custom && custom.trim()) || (picked && picked.value) || "";
    const btn = $("[data-submit]");

    if (!quantity) return showErr("حدد الكمية المطلوبة.");
    if (!phone.trim()) return showErr("أدخل رقم الموبايل.");
    if (!whatsapp.trim()) return showErr("أدخل رقم واتساب.");
    if (address.trim().length < 5) return showErr("اكتب العنوان بالتفصيل.");

    const fd = new FormData();
    fd.append("phone", phone.trim());
    fd.append("whatsapp", whatsapp.trim());
    fd.append("address", address.trim());
    fd.append("quantity", quantity);
    fd.append("color", state.hex);
    fd.append("name", state.printName.trim());
    fd.append("line1", state.printName.trim());
    fd.append("notes", notes.trim());
    fd.append("extras", JSON.stringify({
      nfc: state.nfc, logo: state.logo, qr: state.qr,
      name_print: state.name_print, gloss: state.gloss, matte: state.matte,
      logo_mode: state.logoMode, logo_pos: state.logoPos, logo_size: state.logoSize,
    }));
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
        showErr((data && data.error) || "حصل خطأ، جرّب تاني.");
        if (btn) btn.disabled = false;
        return;
      }
      const wrap = $("[data-order-form-wrap]");
      const done = $("[data-order-done]");
      if (wrap) wrap.hidden = true;
      if (done) done.hidden = false;
    } catch (_) {
      showErr("مشكلة في الاتصال.");
      if (btn) btn.disabled = false;
    }
  });

  fetch("/api/csrf", { credentials: "same-origin" })
    .then((r) => r.json())
    .then((d) => { csrf = d.csrf_token || ""; })
    .catch(() => {});

  paint();
})();
