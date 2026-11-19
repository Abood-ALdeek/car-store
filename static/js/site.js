(function () {
  // Header shadow when the page is scrolled
  var header = document.querySelector("[data-header]");
  function onScroll() { if (header) header.classList.toggle("scrolled", window.scrollY > 10); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var toggle = document.querySelector("[data-menu-toggle]");
  var menu = document.querySelector("[data-menu]");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Car photo gallery
  var mainImg = document.querySelector("[data-gallery-main]");
  document.querySelectorAll(".thumb").forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      if (!mainImg) return;
      mainImg.src = thumb.dataset.src;
      document.querySelectorAll(".thumb").forEach(function (t) { t.classList.remove("active"); });
      thumb.classList.add("active");
    });
  });

  // Share button: native share on phones, copy link elsewhere
  var toast = document.querySelector("[data-toast]");
  document.querySelectorAll("[data-share]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var url = location.href.split("#")[0];
      if (navigator.share) { navigator.share({ title: document.title, url: url }).catch(function () {}); return; }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          if (!toast) return;
          toast.classList.add("show");
          setTimeout(function () { toast.classList.remove("show"); }, 1800);
        });
      }
    });
  });

  // Filter box starts closed on small screens
  var filters = document.querySelector(".filters");
  if (filters && window.matchMedia("(max-width: 1000px)").matches) filters.removeAttribute("open");

  // Loading bar at the top whenever a link is clicked or a form is sent
  var loader = document.querySelector("[data-loader]");
  function startLoader() { if (loader) { loader.classList.remove("run"); void loader.offsetWidth; loader.classList.add("run"); } }
  function stopLoader() { if (loader) loader.classList.remove("run"); }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    if (a.target && a.target !== "_self") return;
    var href = a.getAttribute("href");
    if (!href || href.charAt(0) === "#" || /^(tel:|mailto:|javascript:)/i.test(href)) return;
    if (a.host && a.host !== location.host) return;
    if (a.pathname === location.pathname && a.search === location.search && a.hash) return;
    startLoader();
  });
  document.querySelectorAll("form").forEach(function (f) { f.addEventListener("submit", startLoader); });
  window.addEventListener("pageshow", stopLoader);

  // Photos fade in when loaded
  document.querySelectorAll(".car-img img, .gallery-main img").forEach(function (img) {
    if (img.complete && img.naturalWidth) img.classList.add("loaded");
    else {
      img.addEventListener("load", function () { img.classList.add("loaded"); });
      img.addEventListener("error", function () { img.classList.add("loaded"); });
    }
  });

  // Gallery: smooth switch between photos
  if (mainImg) {
    document.querySelectorAll(".thumb").forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        mainImg.classList.add("switching");
        setTimeout(function () { mainImg.classList.remove("switching"); }, 220);
      });
    });
  }

  // Small stagger for items that sit in the same grid
  document.querySelectorAll(".car-grid, .feature-grid, .steps, .stats").forEach(function (grid) {
    grid.querySelectorAll(".reveal").forEach(function (el, i) { el.style.setProperty("--d", (i % 6) * 0.08 + "s"); });
  });

  // Numbers count up from 0
  function countUp(el) {
    var target = parseInt(el.textContent.replace(/[^0-9]/g, ""), 10);
    if (!target) return;
    var start = null, dur = 1100;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = "0";
    requestAnimationFrame(step);
  }

  // Reveal on scroll
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = document.querySelectorAll(".reveal, .section-head");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("in");
        e.target.querySelectorAll(".stat b, b").forEach(function (b) {
          if (b.closest(".stat")) countUp(b);
        });
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }
})();

// ===== Hero slideshow =====
(function () {
  var root = document.querySelector("[data-slider]");
  if (!root) return;
  var slides = root.querySelectorAll(".slide");
  var bgs = document.querySelectorAll(".hero-bg-img");
  var dots = root.querySelectorAll("[data-dot]");
  var bar = root.querySelector("[data-slide-bar]");
  var chip = root.querySelector("[data-chip]");
  var chipText = chip && chip.querySelector(".hero-chip-text");
  var chipName = root.querySelector("[data-chip-name]");
  var chipPrice = root.querySelector("[data-chip-price]");
  var cond = root.querySelector("[data-slide-cond]");
  var MS = 5500, i = 0, timer = null, paused = false;
  if (slides.length < 2) return;
  root.style.setProperty("--slide-ms", MS + "ms");

  function restartBar() { if (!bar) return; bar.classList.remove("run"); void bar.offsetWidth; if (!paused) bar.classList.add("run"); }

  function show(n) {
    var next = (n + slides.length) % slides.length;
    if (next === i) return;
    slides[i].classList.remove("active"); if (bgs[i]) bgs[i].classList.remove("active"); if (dots[i]) dots[i].classList.remove("active");
    i = next;
    slides[i].classList.add("active"); if (bgs[i]) bgs[i].classList.add("active"); if (dots[i]) dots[i].classList.add("active");
    var s = slides[i];
    if (cond) cond.textContent = s.dataset.cond;
    if (chip) chip.href = s.getAttribute("href");
    if (chipText) {
      chipText.classList.add("swap");
      setTimeout(function () {
        if (chipName) chipName.textContent = s.dataset.name;
        if (chipPrice) chipPrice.textContent = s.dataset.price;
        chipText.classList.remove("swap");
      }, 300);
    }
    restartBar();
  }
  function schedule() { clearInterval(timer); timer = setInterval(function () { if (!paused) show(i + 1); }, MS); restartBar(); }

  root.querySelector("[data-slide-next]").addEventListener("click", function (e) { e.preventDefault(); show(i + 1); schedule(); });
  root.querySelector("[data-slide-prev]").addEventListener("click", function (e) { e.preventDefault(); show(i - 1); schedule(); });
  dots.forEach(function (d) { d.addEventListener("click", function () { show(parseInt(d.dataset.dot, 10)); schedule(); }); });
  var frame = root.querySelector(".hero-frame");
  frame.addEventListener("mouseenter", function () { paused = true; if (bar) bar.style.animationPlayState = "paused"; });
  frame.addEventListener("mouseleave", function () { paused = false; if (bar) bar.style.animationPlayState = "running"; });

  // swipe on phones
  var x0 = null;
  frame.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  frame.addEventListener("touchend", function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) < 40) return;
    var rtl = document.documentElement.dir === "rtl";
    show(i + ((dx < 0) !== rtl ? 1 : -1)); schedule();
  });
  document.addEventListener("visibilitychange", function () { paused = document.hidden; });
  schedule();
})();
