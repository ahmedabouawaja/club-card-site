document.addEventListener("DOMContentLoaded", () => {
  const cms = window.__CMS__ || {};
  const settings = cms.settings || {};
  const stage = document.querySelector("[data-stage]");
  const note = document.querySelector("[data-note]");
  let use = "جيم أو نادي";
  let token = "";

  document.querySelectorAll("[data-cms]").forEach((el) => {
    const key = el.getAttribute("data-cms");
    if (settings[key]) el.textContent = settings[key];
  });

  const usesBox = document.querySelector("[data-flex-uses]");
  const uses = (cms.flexUses && cms.flexUses.length) ? cms.flexUses : [
    { title: "جيم أو نادي", body: "العضو يمرّر الكارت عند الباب بدل الكشف الورق." },
    { title: "هوية موظفين", body: "اسم وصورة ودخول المبنى في كارت واحد." },
    { title: "مدرسة أو مركز", body: "حضور الطالب بالمسح، والكارت يتحمّل الشنطة." },
    { title: "ولاء محل", body: "نفس الكارت للنقاط أو الخصم، لمسة أو QR." },
  ];
  if (usesBox) {
    usesBox.innerHTML = uses.map((u, i) => (
      '<button type="button" class="use' + (i === 0 ? " is-on" : "") + '" data-use="' + u.title.replace(/"/g, "") + '">'
      + "<strong>" + u.title + "</strong><span>" + (u.body || "") + "</span></button>"
    )).join("");
    if (uses[0]) use = uses[0].title;
  }

  const faqsBox = document.querySelector("[data-flex-faqs]");
  const faqs = (cms.faqs && cms.faqs.length) ? cms.faqs : [];
  if (faqsBox) {
    faqsBox.innerHTML = faqs.map((f, i) => (
      "<details" + (i === 0 ? " open" : "") + "><summary>" + f.q + "</summary><p>" + f.a + "</p></details>"
    )).join("") || "<p>أضف أسئلة من لوحة المحتوى.</p>";
  }

  const reviewsBox = document.querySelector("[data-flex-reviews]");
  const reviews = (cms.reviews && cms.reviews.length) ? cms.reviews : [];
  if (reviewsBox) {
    reviewsBox.innerHTML = reviews.map((r) => (
      '<div class="rev"><strong>' + r.title + "</strong><em>" + (r.sub || "") + "</em><p>" + (r.body || "") + "</p></div>"
    )).join("") || "<p>أضف تقييمات من لوحة المحتوى.</p>";
  }

  fetch("/api/csrf", { credentials: "same-origin" })
    .then((r) => r.json())
    .then((data) => { token = data.csrf_token || ""; })
    .catch(() => {});

  const shots = {
    bend: '<div class="card-bend"><div class="l"></div><div class="r"></div></div>',
    door: '<p style="padding:28px;text-align:center;color:#f6ecdf;line-height:1.9">عند الباب<br>العضو يمرّر الكارت ويدخل<br>من غير كشف ورق</p>',
    desk: '<p style="padding:28px;text-align:center;color:#f6ecdf;line-height:1.9">مع الموظف<br>اسم وصورة ودخول المبنى<br>على نفس الكارت</p>',
    scan: '<p style="padding:28px;text-align:center;color:#f6ecdf;line-height:1.9">لمسة NFC أو مسح QR<br>نفس صفحة العضوية أو الهوية<br>حتى لو الموبايل قديم</p>',
  };

  document.querySelectorAll("[data-shot]").forEach((btn) => {
    if (btn.tagName !== "BUTTON") return;
    btn.addEventListener("click", () => {
      document.querySelectorAll(".thumbs button").forEach((b) => b.classList.remove("is-on"));
      btn.classList.add("is-on");
      stage.innerHTML = shots[btn.dataset.shot] || shots.bend;
    });
  });

  document.querySelectorAll(".use").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".use").forEach((b) => b.classList.remove("is-on"));
      btn.classList.add("is-on");
      use = btn.dataset.use;
    });
  });

  document.querySelector("[data-order]")?.addEventListener("click", () => {
    const q = new URLSearchParams({ from: "flex", use: use || "" });
    location.href = "/order?" + q.toString();
  });
});
