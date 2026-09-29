(function loadChrome() {
  if (!document.querySelector('link[href="/static/css/site-nav.css"]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/static/css/site-nav.css";
    document.head.appendChild(link);
  }
  if (!document.querySelector('script[src="/static/js/site-nav.js"]')) {
    const script = document.createElement("script");
    script.src = "/static/js/site-nav.js";
    document.body.appendChild(script);
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  let token = "";

  fetch("/api/csrf", { credentials: "same-origin" })
    .then((r) => r.json())
    .then((data) => { token = data.csrf_token || ""; })
    .catch(() => {});

  const read = (id) => (document.getElementById(id) || {}).value || "";

  const post = (kind, extra) => {
    const body = Object.assign({
      phone: read("cbPhone") || read("fLink") && read("fName"),
      name: read("heroName") || read("fName") || read("l1"),
      line1: read("l1") || read("fName") || read("heroName"),
      line2: read("l2"),
      line3: read("l3"),
      link: read("fLink"),
    }, extra || {});
    if (!body.phone) body.phone = extra && extra.phone;
    return fetch("/api/leads/" + kind, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": token,
      },
      body: JSON.stringify(body),
    }).then((r) => r.json()).catch(() => ({ ok: false }));
  };

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("button, a");
    if (!btn) return;
    const label = (btn.textContent || "").replace(/\s+/g, " ").trim();

    if (label.includes("اطلب مكالمة")) {
      const phone = read("cbPhone");
      if (!phone) return;
      post("callback", {
        phone,
        audience: document.body.innerText.includes("شركات") ? undefined : undefined,
        line1: read("l1"),
        line2: read("l2"),
        line3: read("l3"),
        notes: "طلب مكالمة من الصفحة الرئيسية",
      });
    }

    if (label.includes("أرسل طلبك على واتساب") || label.includes("أرسل الطلب على واتساب") || label.includes("راسلنا الآن") || label.includes("اطلب معاينة على واتساب")) {
      const kind = location.pathname.indexOf("personal") !== -1
        ? "personal"
        : location.pathname.indexOf("readers") !== -1
          ? "reader"
          : "quote";
      post(kind, {
        phone: read("cbPhone"),
        notes: "تم التحويل إلى واتساب",
      });
    }
  });
});
