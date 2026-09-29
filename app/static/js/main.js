// Visual behavior only. Auth, tiers, and CSRF stay on the server.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  document.querySelectorAll("form[action*='/freeze']").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm("Are you sure?")) e.preventDefault();
    });
  });

  document.querySelectorAll(".card-scene").forEach(setupTilt);
  const scene = document.querySelector("[data-card]");
  if (scene) setupFlip(scene);
  setupStudio();
  setupLang();
  setupNav();
  setupViewer();
  setupDesigner();
});

function setupLang() {
  const btn = document.querySelector("[data-lang]");
  const apply = (lang) => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "en" ? "ltr" : "rtl";
    localStorage.setItem("cardlink-lang", lang);
    document.querySelectorAll("[data-ar]").forEach((el) => {
      const next = lang === "en" ? el.dataset.en : el.dataset.ar;
      if (next) el.textContent = next;
    });
  };
  apply(localStorage.getItem("cardlink-lang") || "ar");
  if (btn) btn.addEventListener("click", () => {
    apply(document.documentElement.lang === "ar" ? "en" : "ar");
    document.dispatchEvent(new Event("cardlink-lang"));
  });
}

function setupNav() {
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => nav.classList.toggle("is-open"));
}

function setupViewer() {
  const card = document.querySelector(".viewer [data-nfc]");
  if (!card) return;
  const dots = document.querySelectorAll("[data-angle-dots] button");
  const views = [
    { yaw: -26, pitch: 10 },
    { yaw: 12, pitch: 6 },
    { yaw: 180, pitch: 8 },
    { yaw: 208, pitch: 10 },
  ];
  let index = 0;
  const paint = () => {
    const view = views[index];
    card.style.setProperty("--yaw", view.yaw + "deg");
    card.style.setProperty("--pitch", view.pitch + "deg");
    dots.forEach((dot, i) => dot.classList.toggle("is-on", i === index));
  };
  const move = (step) => {
    index = (index + step + views.length) % views.length;
    paint();
  };
  document.querySelector("[data-angle-prev]")?.addEventListener("click", () => move(-1));
  document.querySelector("[data-angle-next]")?.addEventListener("click", () => move(1));
  dots.forEach((dot, i) => dot.addEventListener("click", () => { index = i; paint(); }));
  paint();
}

function setupDesigner() {
  const form = document.querySelector("[data-designer]");
  if (!form) return;
  const titles = [
    { ar: "اختر قالب البطاقة", en: "Choose a card template" },
    { ar: "أضف شعارك وبياناتك", en: "Add your logo and details" },
    { ar: "حدد الكمية والتواصل", en: "Set quantity and contact" },
    { ar: "راجع الطلب وأرسله", en: "Review and send" },
  ];
  const skins = {
    classic: { ar: "كلاسيك أبيض", en: "Classic white" },
    black: { ar: "معدني أسود", en: "Metal black" },
    gold: { ar: "ذهبي فخم", en: "Luxury gold" },
    navy: { ar: "أزرق راقي", en: "Deep navy" },
  };
  const preview = form.querySelector("[data-nfc]");
  const title = form.querySelector("[data-step-title]");
  const panes = form.querySelectorAll("[data-pane]");
  const marks = document.querySelectorAll("[data-steps] li");
  const nextBtn = form.querySelector("[data-next]");
  const prevBtn = form.querySelector("[data-prev]");
  const submitBtn = form.querySelector("[data-submit]");
  const templateInput = form.querySelector("[data-template-input]");
  const brandInput = form.querySelector("[name=brand]");
  const logoInput = form.querySelector("[name=logo]");
  const sinceInput = form.querySelector("[name=since]");
  const qtyInput = form.querySelector("[name=quantity]");
  const phoneInput = form.querySelector("[name=phone]");
  let step = 1;

  const lang = () => document.documentElement.lang === "en" ? "en" : "ar";
  const show = () => {
    panes.forEach((pane) => pane.classList.toggle("is-on", Number(pane.dataset.pane) === step));
    marks.forEach((mark, i) => mark.classList.toggle("is-on", i + 1 === step));
    title.textContent = titles[step - 1][lang()];
    prevBtn.hidden = step === 1;
    nextBtn.hidden = step === 4;
    submitBtn.hidden = step !== 4;
    form.querySelector("[data-review=template]").textContent = skins[templateInput.value][lang()];
    form.querySelector("[data-review=brand]").textContent = brandInput.value;
    form.querySelector("[data-review=qty]").textContent = qtyInput.value;
    form.querySelector("[data-review=phone]").textContent = phoneInput.value || "—";
  };
  const paintCard = () => {
    preview.dataset.skin = templateInput.value;
    setText(preview, "brand", brandInput.value || "كارلينك");
    setText(preview, "logo", logoInput.value || "[YOUR LOGO]");
    setText(preview, "since", "MEMBER SINCE " + (sinceInput.value || "2024"));
  };

  form.querySelectorAll("[data-skin]").forEach((btn) => {
    btn.addEventListener("click", () => {
      form.querySelectorAll("[data-skin]").forEach((other) => other.classList.remove("is-on"));
      btn.classList.add("is-on");
      templateInput.value = btn.dataset.skin;
      paintCard();
      show();
    });
  });
  [brandInput, logoInput, sinceInput, qtyInput, phoneInput].forEach((input) => {
    input.addEventListener("input", () => { paintCard(); show(); });
  });
  nextBtn.addEventListener("click", () => { if (step < 4) { step += 1; show(); } });
  prevBtn.addEventListener("click", () => { if (step > 1) { step -= 1; show(); } });
  document.addEventListener("cardlink-lang", show);
  paintCard();
  show();
}

function setupTilt(scene) {
  const rig = scene.querySelector(".card-rig");
  if (!rig || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const max = scene.classList.contains("is-back-only") ? 14 : 18;

  const apply = (clientX, clientY) => {
    const rect = scene.getBoundingClientRect();
    const px = (clientX - rect.left) / rect.width - 0.5;
    const py = (clientY - rect.top) / rect.height - 0.5;
    rig.style.setProperty("--tilt-y", (px * max).toFixed(2) + "deg");
    rig.style.setProperty("--tilt-x", (-py * max * 0.75).toFixed(2) + "deg");
    scene.style.setProperty("--sheen", (px * 70).toFixed(1) + "%");
  };

  scene.addEventListener("pointermove", (e) => {
    scene.classList.add("is-tilting");
    apply(e.clientX, e.clientY);
  });
  scene.addEventListener("pointerleave", () => {
    scene.classList.remove("is-tilting");
    rig.style.setProperty("--tilt-x", "0deg");
    rig.style.setProperty("--tilt-y", "0deg");
    scene.style.setProperty("--sheen", "-40%");
  });
}

function setupFlip(scene) {
  const flipBtn = document.querySelector("[data-flip]");
  const pauseBtn = document.querySelector("[data-pause]");
  if (!flipBtn && !pauseBtn) return;

  const flip = () => {
    const showingBack = scene.classList.contains("is-manual")
      ? scene.classList.contains("is-flipped")
      : false;
    scene.classList.add("is-manual", "is-paused");
    scene.classList.toggle("is-flipped", !showingBack);
    if (pauseBtn) pauseBtn.textContent = "Resume rotation";
  };

  scene.addEventListener("click", flip);
  if (flipBtn) flipBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    flip();
  });
  if (pauseBtn) {
    pauseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const paused = scene.classList.toggle("is-paused");
      if (!paused) scene.classList.remove("is-manual");
      pauseBtn.textContent = paused ? "Resume rotation" : "Pause rotation";
    });
  }
}

function setupStudio() {
  const form = document.getElementById("card-details");
  const rows = document.querySelectorAll("[data-member]");
  const addToggle = document.querySelector("[data-add-toggle]");
  const addForm = document.getElementById("add-member");
  if (addToggle && addForm) {
    addToggle.addEventListener("click", () => {
      addForm.hidden = !addForm.hidden;
      if (!addForm.hidden) addForm.querySelector("input")?.focus();
    });
  }
  if (!form || !rows.length) return;

  const benefits = readBenefits();
  const nameInput = form.querySelector("[name=name]");
  const numberInput = form.querySelector("[name=member_no]");
  const validInput = form.querySelector("[name=valid_thru]");
  const tierInput = form.querySelector("[name=tier]");
  const accentInput = form.querySelector("[name=accent]");
  const status = form.querySelector("[data-save-status]");
  let saveTimer = null;

  const paint = () => {
    const tier = tierInput.value;
    const pack = benefits[tier] || benefits.member;
    const frozen = currentFrozen();
    applyCard({
      name: nameInput.value,
      number: numberInput.value,
      valid: validInput.value,
      tier,
      accent: accentInput.value,
      tierLabel: (frozen ? pack.pill + " · FROZEN" : pack.pill),
      benefitsTitle: pack.title,
      benefits: pack.items,
    });
  };

  const queueSave = () => {
    paint();
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveDetails, 450);
  };

  rows.forEach((row) => {
    row.addEventListener("click", () => {
      rows.forEach((other) => other.classList.remove("is-selected"));
      row.classList.add("is-selected");
      nameInput.value = row.dataset.name || "";
      numberInput.value = row.dataset.number || "";
      validInput.value = row.dataset.valid || "";
      tierInput.value = row.dataset.tier || "member";
      accentInput.value = row.dataset.accent || "lime";
      form.action = "/admin/member/" + row.dataset.id + "/details";
      const freezeForm = document.getElementById("freeze-form");
      if (freezeForm) {
        freezeForm.action = "/admin/member/" + row.dataset.id + "/freeze";
        const freezeBtn = freezeForm.querySelector("button");
        if (freezeBtn) freezeBtn.textContent = row.dataset.frozen === "1" ? "Unfreeze card" : "Freeze card";
      }
      syncTierButtons();
      syncSwatches();
      paint();
    });
  });

  form.querySelectorAll(".tier-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      tierInput.value = btn.dataset.tier;
      syncTierButtons();
      queueSave();
    });
  });
  form.querySelectorAll(".swatch").forEach((btn) => {
    btn.addEventListener("click", () => {
      accentInput.value = btn.dataset.accent;
      syncSwatches();
      queueSave();
    });
  });
  [nameInput, numberInput, validInput].forEach((input) => {
    input.addEventListener("input", queueSave);
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    saveDetails();
  });

  function syncTierButtons() {
    form.querySelectorAll(".tier-btn").forEach((btn) => {
      btn.classList.toggle("is-selected", btn.dataset.tier === tierInput.value);
    });
  }
  function syncSwatches() {
    form.querySelectorAll(".swatch").forEach((btn) => {
      btn.classList.toggle("is-selected", btn.dataset.accent === accentInput.value);
    });
  }
  function currentFrozen() {
    const selected = document.querySelector("[data-member].is-selected");
    return selected && selected.dataset.frozen === "1";
  }

  async function saveDetails() {
    if (!form.action || form.action.endsWith("#")) return;
    status.textContent = "Saving…";
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "fetch" },
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        status.textContent = data.error || "Could not save.";
        return;
      }
      status.textContent = "Saved";
      const selected = document.querySelector("[data-member].is-selected");
      if (selected) {
        selected.dataset.name = nameInput.value;
        selected.dataset.number = numberInput.value;
        selected.dataset.valid = validInput.value;
        selected.dataset.tier = tierInput.value;
        selected.dataset.accent = accentInput.value;
        const who = selected.querySelector(".who");
        const tierName = selected.querySelector(".tier-name");
        const dot = selected.querySelector(".dot");
        if (who) who.textContent = nameInput.value;
        if (tierName) tierName.textContent = tierInput.value.toUpperCase();
        if (dot) dot.className = "dot dot-tier-" + tierInput.value;
      }
    } catch (err) {
      status.textContent = "Could not save.";
    }
  }
}

function applyCard(data) {
  const scene = document.querySelector("[data-card]");
  if (!scene) return;
  scene.dataset.tier = data.tier;
  scene.dataset.accent = data.accent;
  setText(scene, "name", data.name || "[MEMBER NAME]");
  setText(scene, "number", data.number || "0000 0000 0000");
  setText(scene, "valid", data.valid || "[MM/YY]");
  setText(scene, "tier-label", data.tierLabel || "MEMBER");
  setText(scene, "benefits-title", data.benefitsTitle || "MEMBER BENEFITS");
  const list = scene.querySelector('[data-bind="benefits"]');
  if (list) {
    list.replaceChildren();
    (data.benefits || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    });
  }
}

function setText(root, key, value) {
  root.querySelectorAll('[data-bind="' + key + '"]').forEach((el) => {
    el.textContent = value;
  });
}

function readBenefits() {
  const node = document.getElementById("tier-benefits");
  if (!node) return {};
  try {
    return JSON.parse(node.textContent || "{}");
  } catch (err) {
    return {};
  }
}
