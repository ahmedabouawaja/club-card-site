function mountDock() {
  if (document.querySelector(".cl-dock") || !document.body) return;
  const path = location.pathname.replace(/\/$/, "") || "/";
  const narrow = window.matchMedia("(max-width: 520px)").matches;
  const items = narrow
    ? [
        ["/", "الرئيسية"],
        ["/#studio", "صمّم"],
        ["/personal", "أفراد"],
        ["/#order", "اطلب", "cta"],
      ]
    : [
        ["/", "الرئيسية"],
        ["/flex", "فليكس"],
        ["/personal", "للأفراد"],
        ["/readers", "أجهزة الدخول"],
        ["/#studio", "صمّم كارتك"],
        ["/#order", "اطلب الآن", "cta"],
      ];
  const nav = document.createElement("nav");
  nav.className = "cl-dock";
  nav.setAttribute("aria-label", "تنقل الموقع");
  items.forEach(([href, label, extra]) => {
    const a = document.createElement("a");
    a.href = href;
    a.textContent = label;
    if (extra) a.className = extra;
    const dest = href.split("#")[0] || "/";
    if (dest === path || (path === "/" && href === "/")) a.classList.add("is-on");
    if (path === "/flex" && href === "/flex") a.classList.add("is-on");
    nav.appendChild(a);
  });
  document.body.appendChild(nav);
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountDock);
} else {
  mountDock();
}
