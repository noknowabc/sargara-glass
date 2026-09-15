/* ==========================================================================
   SARGARA® — site behaviour
   Vanilla JS, no dependencies.
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel));
  };

  /* ---------------------------------------------------------------- header */
  function initHeader() {
    var header = $(".site-header");
    if (!header) return;
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------------------------------------------------------------- drawer */
  function initDrawer() {
    var drawer = $("#drawer");
    var toggle = $(".nav-toggle");
    if (!drawer || !toggle) return;

    var open = function () {
      drawer.classList.add("is-open");
      doc.body.classList.add("is-locked");
      toggle.setAttribute("aria-expanded", "true");
      var first = drawer.querySelector("a, button");
      if (first) first.focus();
    };
    var close = function () {
      drawer.classList.remove("is-open");
      doc.body.classList.remove("is-locked");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", open);
    $$("[data-drawer-close]", drawer).forEach(function (el) {
      el.addEventListener("click", close);
    });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });
  }

  /* ------------------------------------------------------------------ lang */
  function initLang() {
    var wrap = $(".lang");
    if (!wrap) return;
    var trigger = $(".lang__current", wrap);
    var label = $("[data-lang-label]", wrap);

    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      wrap.classList.toggle("is-open");
      trigger.setAttribute("aria-expanded", wrap.classList.contains("is-open") ? "true" : "false");
    });
    doc.addEventListener("click", function () {
      wrap.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
    });

    $$("button[data-lang]", wrap).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var code = btn.getAttribute("data-lang");
        window.SARGARA_I18N.apply(code);
        if (label) label.textContent = btn.getAttribute("data-lang-name");
        $$("button[data-lang]", wrap).forEach(function (b) {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        wrap.classList.remove("is-open");
        try { window.localStorage.setItem("sargara-lang", code); } catch (err) {}
      });
    });

    var saved = null;
    try { saved = window.localStorage.getItem("sargara-lang"); } catch (err) {}
    if (saved && saved !== "en") {
      var target = $('button[data-lang="' + saved + '"]', wrap);
      if (target) target.click();
    }
  }

  /* ---------------------------------------------------------------- reveal */
  function initReveal() {
    var items = $$("[data-reveal]");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var passed = entry.boundingClientRect.top < 0;
          if (!entry.isIntersecting && !passed) return;
          var el = entry.target;
          var delay = parseInt(el.getAttribute("data-reveal-delay") || "0", 10);
          setTimeout(function () { el.classList.add("is-in"); }, delay);
          io.unobserve(el);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    items.forEach(function (el) { io.observe(el); });

    /* safety net: never leave content invisible after a fast jump or hash link */
    var sweep = function () {
      items.forEach(function (el) {
        if (el.classList.contains("is-in")) return;
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.95) {
          el.classList.add("is-in");
          io.unobserve(el);
        }
      });
    };
    window.addEventListener("load", function () { setTimeout(sweep, 200); });
    window.addEventListener("scroll", sweep, { passive: true });
    window.addEventListener("hashchange", function () { setTimeout(sweep, 250); });
    setTimeout(sweep, 500);
  }

  /* --------------------------------------------------------------- catalog */
  function initCatalog() {
    var grid = $("[data-catalog]");
    if (!grid) return;

    var cards = $$(".product-card", grid);
    var filters = $$("[data-filter]");
    var search = $("[data-catalog-search]");
    var count = $("[data-catalog-count]");
    var empty = $(".catalog-empty", grid);
    var state = { cat: "all", q: "" };

    function apply() {
      var visible = 0;
      cards.forEach(function (card) {
        var cats = (card.getAttribute("data-cats") || "").split(/\s+/);
        var hay = (card.getAttribute("data-search") || "").toLowerCase();
        var okCat = state.cat === "all" || cats.indexOf(state.cat) !== -1;
        var okQ = !state.q || hay.indexOf(state.q) !== -1;
        var show = okCat && okQ;
        card.style.display = show ? "" : "none";
        if (show) visible++;
      });
      if (empty) empty.hidden = visible !== 0;
      if (count) count.textContent = String(visible);
    }

    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filters.forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        state.cat = btn.getAttribute("data-filter");
        apply();
      });
    });

    if (search) {
      search.addEventListener("input", function () {
        state.q = search.value.trim().toLowerCase();
        apply();
      });
    }

    var initial = new URLSearchParams(window.location.search).get("cat");
    if (initial) {
      var match = filters.filter(function (b) {
        return b.getAttribute("data-filter") === initial;
      })[0];
      if (match) match.click();
    }
    apply();
  }

  /* --------------------------------------------------------------- gallery */
  function initGallery() {
    var gallery = $("[data-gallery]");
    if (!gallery) return;
    var main = $(".gallery__main img", gallery);
    var thumbs = $$(".gallery__thumb", gallery);
    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        var src = thumb.getAttribute("data-src");
        if (!src || !main) return;
        main.src = src;
        thumbs.forEach(function (t) { t.classList.remove("is-active"); });
        thumb.classList.add("is-active");
      });
    });
  }

  /* ----------------------------------------------------------------- forms */
  function initForms() {
    $$("form[data-validate]").forEach(function (form) {
      var alertBox = $("[data-form-alert]", form);
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var valid = true;

        $$(".field", form).forEach(function (field) {
          var input = field.querySelector("input, select, textarea");
          if (!input) return;
          var required = input.hasAttribute("required");
          var value = (input.value || "").trim();
          var ok = true;

          if (required && !value) ok = false;
          if (ok && input.type === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) ok = false;
          if (ok && input.type === "tel" && value && value.replace(/\D/g, "").length < 6) ok = false;

          field.classList.toggle("has-error", !ok);
          if (!ok) {
            valid = false;
            if (!field.dataset.touched) {
              input.addEventListener("input", function handler() {
                var still = input.hasAttribute("required") && !(input.value || "").trim();
                field.classList.toggle("has-error", still);
              });
            }
          }
        });

        if (!valid) {
          var firstBad = $(".field.has-error input, .field.has-error select, .field.has-error textarea", form);
          if (firstBad) firstBad.focus();
          return;
        }

        var btn = form.querySelector('button[type="submit"]');
        var original = btn ? btn.textContent : "";
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Sending…";
        }

        window.setTimeout(function () {
          if (btn) {
            btn.disabled = false;
            btn.textContent = original;
          }
          if (alertBox) {
            alertBox.classList.add("is-visible");
            alertBox.scrollIntoView({ block: "center", behavior: "smooth" });
          }
          form.reset();
        }, 900);
      });
    });
  }

  /* ---------------------------------------------------------------- floaty */
  function initFloaty() {
    var top = $(".floaty--top");
    if (!top) return;
    var onScroll = function () {
      top.classList.toggle("is-visible", window.scrollY > 500);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    top.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ------------------------------------------------------------------ misc */
  function initMisc() {
    $$("[data-year]").forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* ------------------------------------------------------------------ boot */
  function boot() {
    initHeader();
    initDrawer();
    initLang();
    initReveal();
    initCatalog();
    initGallery();
    initForms();
    initFloaty();
    initMisc();
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
