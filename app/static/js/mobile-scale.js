(function () {
  function canvases() {
    var nodes = document.querySelectorAll("div");
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.getAttribute("data-dc-root") != null) {
        out.push(el);
        continue;
      }
      var w = (el.getAttribute("style") || "").replace(/\s/g, "");
      if (/width:1440px/i.test(w)) {
        el.setAttribute("data-dc-root", "");
        out.push(el);
      }
    }
    return out;
  }

  function designHeight(el) {
    var m = (el.getAttribute("style") || "").match(/height:\s*(\d+)px/i);
    if (m) return Number(m[1]);
    return el.scrollHeight || 2000;
  }

  function fitOne(el) {
    var wrap = el.parentElement;
    if (!wrap || !wrap.classList.contains("dc-fit")) {
      wrap = document.createElement("div");
      wrap.className = "dc-fit";
      el.parentNode.insertBefore(wrap, el);
      wrap.appendChild(el);
    }
    var vw = Math.max(320, Math.min(window.innerWidth, document.documentElement.clientWidth || window.innerWidth));
    var scale = Math.min(1, vw / 1440);
    el.style.setProperty("--dc-scale", String(scale));
    wrap.style.height = Math.ceil(designHeight(el) * scale) + "px";
  }

  function fitAll() {
    canvases().forEach(fitOne);
  }

  var t;
  function schedule() {
    clearTimeout(t);
    t = setTimeout(fitAll, 50);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fitAll);
  } else {
    fitAll();
  }
  window.addEventListener("resize", schedule);
  window.addEventListener("orientationchange", schedule);
  setTimeout(fitAll, 300);
  setTimeout(fitAll, 1200);
})();
