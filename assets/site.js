// Menu button: opens the full menu over the page.
(function () {
  var btn = document.getElementById("menu-toggle");
  var menu = document.getElementById("site-menu");
  if (!btn || !menu) return;
  var behind = document.querySelectorAll("main, footer, .status-banner, .skip-link");
  function setOpen(open) {
    menu.hidden = !open;
    btn.setAttribute("aria-expanded", String(open));
    btn.setAttribute("aria-label", open ? "Close menu" : "Menu");
    btn.title = open ? "Close menu" : "Menu";
    document.body.classList.toggle("menu-open", open);
    behind.forEach(function (el) { el.inert = open; });
    if (open) { var first = menu.querySelector("a"); if (first) first.focus(); }
  }
  btn.addEventListener("click", function () { setOpen(menu.hidden); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !menu.hidden) { setOpen(false); btn.focus(); }
  });
})();

// Small header after scrolling down. Two thresholds so it does not flicker.
(function () {
  var header = document.querySelector(".site-header");
  if (!header) return;
  var compact = false, ticking = false;
  function check() {
    ticking = false;
    var y = window.scrollY;
    if (!compact && y > 160) { compact = true; header.classList.add("site-header--compact"); }
    else if (compact && y < 40) { compact = false; header.classList.remove("site-header--compact"); }
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(check); }
  }, { passive: true });
  check();
})();

// Section tabs: sit under the header, whatever its height, mark the section
// in view and take the colours of the page under them.
(function () {
  var nav = document.querySelector(".section-tabs");
  var header = document.querySelector(".site-header");
  if (!nav || !header) return;
  var root = document.documentElement;
  new ResizeObserver(function () {
    root.style.setProperty("--header-h", header.offsetHeight + "px");
    root.style.setProperty("--tabs-h", nav.offsetHeight + "px");
    mark();
  }).observe(header, { box: "border-box" });
  var links = [].slice.call(nav.querySelectorAll("a"));
  var pages = [].slice.call(document.querySelectorAll(".typeface__page"));
  var colours = ["--color-bg", "--color-text", "--color-accent", "--color-rule"];
  var ticking = false;
  function mark() {
    ticking = false;
    var line = nav.getBoundingClientRect().bottom + 1, cur = links[0], seen = null;
    links.forEach(function (a) {
      if (document.getElementById(a.hash.slice(1)).getBoundingClientRect().top <= window.innerHeight / 3) cur = a;
    });
    pages.forEach(function (p) {
      var box = p.getBoundingClientRect();
      if (box.top <= line + 1 && box.bottom > line) seen = p;
    });
    links.forEach(function (a) {
      if (a === cur) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    var style = seen && getComputedStyle(seen);
    colours.forEach(function (c) {
      if (style) nav.style.setProperty(c, style.getPropertyValue(c));
      else nav.style.removeProperty(c);
    });
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(mark); }
  }, { passive: true });
  mark();
})();

// Typefaces: specimen words grow to fill the line, each meta line shows the
// size in use, and a click in the glyph grid shows that glyph large.
(function () {
  var fits = [].slice.call(document.querySelectorAll("[data-fit]"));
  var specimens = [].slice.call(document.querySelectorAll(".typeface__specimen"));
  if (!fits.length && !specimens.length) return;
  var first = document.querySelector(".typeface__page--hero");
  function fit() {
    // The first title page ends at the bottom of the first screen, under the page title.
    var room = 0;
    if (first) {
      first.style.minHeight = "";
      var top = first.getBoundingClientRect().top + window.scrollY;
      if (top < window.innerHeight / 2) {
        first.style.minHeight = (window.innerHeight - top) + "px";
        room = window.innerHeight - top - 2 * parseFloat(getComputedStyle(first).paddingBottom);
      }
    }
    fits.forEach(function (el) {
      el.classList.add("is-fitted");
      el.style.fontSize = "100px";
      var w = el.firstElementChild.getBoundingClientRect().width;
      var max = Number(el.getAttribute("data-fit"));
      if (room && el.parentNode === first) max = Math.min(max, room / 1.2);
      el.style.fontSize = Math.min(99 * el.clientWidth / w, max) + "px";
    });
    specimens.forEach(function (fig) {
      var size = parseFloat(getComputedStyle(fig.querySelector(".typeface__sample")).fontSize);
      fig.querySelector("[data-size]").textContent = Math.round(size) + " px";
    });
  }
  var ticking = false;
  window.addEventListener("resize", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; fit(); }); }
  });
  document.fonts.ready.then(fit);
})();

document.querySelectorAll(".typeface__glyphs").forEach(function (box) {
  var big = box.querySelector(".typeface__box text");
  var code = box.querySelector("[data-code]"), name = box.querySelector("[data-name]");
  box.querySelectorAll(".typeface__glyph").forEach(function (btn) {
    btn.addEventListener("click", function () {
      box.querySelector('.typeface__glyph[aria-pressed="true"]').setAttribute("aria-pressed", "false");
      btn.setAttribute("aria-pressed", "true");
      big.textContent = btn.textContent;
      code.textContent = btn.getAttribute("data-code");
      name.textContent = btn.getAttribute("data-name");
    });
  });
});

// Search page: filters search.json in the browser.
(function () {
  var list = document.getElementById("search-results");
  if (!list) return;
  var status = document.getElementById("search-status");
  var input = document.getElementById("search-page-q");
  var q = (new URLSearchParams(location.search).get("q") || "").trim();
  input.value = q;
  if (!q) { input.focus(); return; }
  function norm(s) { return (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }
  status.textContent = "Searching…";
  fetch(list.getAttribute("data-index")).then(function (r) { return r.json(); }).then(function (items) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    var hits = [];
    items.forEach(function (it) {
      var t = norm(it.t), e = norm(it.e), x = norm(it.x), score = 0;
      for (var i = 0; i < terms.length; i++) {
        var w = terms[i];
        if (t.indexOf(w) < 0 && e.indexOf(w) < 0 && x.indexOf(w) < 0) return;
        score += (t.indexOf(w) >= 0 ? 10 : 0) + (e.indexOf(w) >= 0 ? 3 : 0) + (x.indexOf(w) >= 0 ? 1 : 0);
      }
      hits.push({ it: it, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    list.textContent = "";
    hits.slice(0, 50).forEach(function (h) {
      var li = document.createElement("li"); li.className = "card";
      var h2 = document.createElement("h2"); h2.className = "card__title";
      var a = document.createElement("a"); a.href = h.it.u; a.textContent = h.it.t;
      h2.appendChild(a); li.appendChild(h2);
      if (h.it.s) { var m = document.createElement("p"); m.className = "card__meta"; m.textContent = h.it.s; li.appendChild(m); }
      if (h.it.e) { var p = document.createElement("p"); p.className = "card__text"; p.textContent = h.it.e; li.appendChild(p); }
      list.appendChild(li);
    });
    status.textContent = hits.length === 0 ? "No results for “" + q + "”." :
      hits.length + (hits.length === 1 ? " result" : " results") + " for “" + q + "”.";
  }).catch(function () { status.textContent = "Search could not load. Please try again."; });
})();

// Theme toggle, as on psubhashish.com. The choice is kept in this browser.
(function () {
  var html = document.documentElement;
  var btn = document.getElementById("theme-toggle");
  if (!btn) return;
  function current() {
    return html.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function update(theme) {
    var label = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
    btn.setAttribute("aria-label", label);
    btn.title = label;
  }
  update(current());
  btn.addEventListener("click", function () {
    var next = current() === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    try { localStorage.setItem("site-theme", next); } catch (e) {}
    update(next);
    spotifyTheme();
  });
  spotifyTheme();

  // Spotify players follow the theme: theme=0 is Spotify's dark player.
  function spotifyTheme() {
    var dark = current() === "dark";
    document.querySelectorAll("iframe[data-spotify]").forEach(function (f) {
      var src = "https://open.spotify.com/embed/episode/" + f.getAttribute("data-spotify") +
        "?utm_source=generator" + (dark ? "&theme=0" : "");
      if (f.src !== src) f.src = src;
    });
  }
})();

// Click-to-play video: the YouTube player loads only when someone asks for it.
document.querySelectorAll(".embed-play").forEach(function (link) {
  link.addEventListener("click", function (event) {
    event.preventDefault();
    var frame = document.createElement("iframe");
    frame.src = link.getAttribute("data-embed");
    frame.title = link.getAttribute("data-title") || "Video";
    frame.allow = "autoplay; fullscreen; picture-in-picture";
    frame.allowFullscreen = true;
    link.replaceWith(frame);
    frame.focus();
  });
});

// Copy buttons (ARK permalink, citation).
document.querySelectorAll(".copy-btn[data-copy], .copy-id[data-copy], .citation-copy").forEach(function (btn) {
  btn.addEventListener("click", function () {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(btn.getAttribute("data-copy")).then(function () {
      btn.classList.add("copied");
      setTimeout(function () { btn.classList.remove("copied"); }, 1200);
    });
  });
});

// Citation block, same behaviour as the Archiving the Present manual.
document.querySelectorAll(".citation-block").forEach(function (block) {
  var citations = JSON.parse(block.getAttribute("data-citation"));
  var accessed = new Date().toLocaleDateString("en-GB", { year: "numeric", month: "long", day: "numeric" });
  var select = block.querySelector(".citation-style");
  var pre = block.querySelector(".citation-text");
  var copyBtn = block.querySelector(".citation-copy");

  function render() {
    var text = citations[select.value].split("__ACCESSED__").join(accessed);
    pre.textContent = text;
    copyBtn.setAttribute("data-copy", text);
  }
  select.addEventListener("change", render);
  render();

  block.querySelector(".citation-download").addEventListener("click", function () {
    var text = citations.bibtex.split("__ACCESSED__").join(accessed);
    var url = URL.createObjectURL(new Blob([text], { type: "application/x-bibtex" }));
    var a = document.createElement("a");
    a.href = url;
    a.download = (block.getAttribute("data-id") || "citation") + ".bib";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
});

// Section links: a "#" after each heading copies a link to that section.
document.querySelectorAll("main h2[id], main h3[id]").forEach(function (h) {
  if (h.querySelector(".heading-anchor") || h.closest(".film-hero")) return;
  var a = document.createElement("a");
  a.href = "#" + h.id;
  a.className = "heading-anchor";
  a.setAttribute("aria-label", "Copy link to this section: " + h.textContent.trim());
  a.title = "Copy link";
  a.appendChild(document.createTextNode("#"));
  var copied = document.createElement("span");
  copied.className = "anchor-copied";
  copied.textContent = "Copied";
  a.appendChild(copied);
  h.appendChild(a);
  a.addEventListener("click", function (e) {
    var url = location.origin + location.pathname + "#" + h.id;
    if (!navigator.clipboard) return;
    e.preventDefault();
    history.replaceState(null, "", "#" + h.id);
    navigator.clipboard.writeText(url).then(function () {
      a.classList.add("just-copied");
      setTimeout(function () { a.classList.remove("just-copied"); }, 1500);
    });
  });
});

// Image viewer: stills and posters open large on the same page.
// Without JavaScript the link opens the image itself.
(function () {
  var groups = {};
  document.querySelectorAll("a[data-viewer]").forEach(function (a) {
    var g = a.getAttribute("data-viewer");
    (groups[g] = groups[g] || []).push(a);
  });
  if (!Object.keys(groups).length || typeof HTMLDialogElement !== "function") return;

  var dialog = document.createElement("dialog");
  dialog.className = "viewer";
  dialog.setAttribute("aria-label", "Image viewer");
  dialog.innerHTML =
    '<div class="viewer__inner">' +
    '<div class="viewer__bar"><p class="viewer__count" aria-live="polite"></p>' +
    '<button type="button" class="viewer__close">Close</button></div>' +
    '<figure class="viewer__figure"><img alt=""></figure>' +
    '<div class="viewer__nav"><button type="button" class="viewer__prev">Previous</button>' +
    '<button type="button" class="viewer__next">Next</button></div></div>';
  document.body.appendChild(dialog);
  var img = dialog.querySelector("img");
  var count = dialog.querySelector(".viewer__count");
  var prev = dialog.querySelector(".viewer__prev");
  var next = dialog.querySelector(".viewer__next");
  var list = [], index = 0, opener = null;

  function show(i) {
    index = (i + list.length) % list.length;
    var link = list[index];
    var thumb = link.querySelector("img");
    img.src = link.getAttribute("href");
    img.alt = thumb ? thumb.alt : "";
    count.textContent = (img.alt || "Image") + " (" + (index + 1) + " of " + list.length + ")";
    prev.hidden = next.hidden = list.length < 2;
  }

  Object.keys(groups).forEach(function (g) {
    groups[g].forEach(function (link, i) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        list = groups[g];
        opener = link;
        show(i);
        dialog.showModal();
        dialog.querySelector(".viewer__close").focus();
      });
    });
  });
  prev.addEventListener("click", function () { show(index - 1); });
  next.addEventListener("click", function () { show(index + 1); });
  dialog.querySelector(".viewer__close").addEventListener("click", function () { dialog.close(); });
  dialog.addEventListener("click", function (e) {
    if (e.target === dialog || e.target.classList.contains("viewer__figure")) dialog.close();
  });
  dialog.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); }
    if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); }
  });
  dialog.addEventListener("close", function () {
    img.removeAttribute("src");
    if (opener) setTimeout(function () { opener.focus(); }, 0);
  });
})();

// Type tester: the slider sets the sample size; typing updates the waterfall.
(function () {
  document.querySelectorAll(".specimen").forEach(function (box) {
    var text = box.querySelector(".specimen__text");
    var range = box.querySelector(".specimen__range");
    var lines = box.querySelectorAll(".specimen__line");
    range.addEventListener("input", function () { text.style.fontSize = range.value + "px"; });
    var reset = box.querySelector(".specimen__reset");
    if (!reset) return;  // preview font: size only
    text.addEventListener("input", function () {
      var t = text.textContent;
      lines.forEach(function (l) { l.textContent = t; });
    });
    reset.addEventListener("click", function () {
      text.textContent = text.dataset.original;
      lines.forEach(function (l) { l.textContent = text.dataset.original; });
    });
  });
})();

// Font-to-Unicode converters (Santali, Ho). Jnanaranjan Sahu's server does the conversion.
document.querySelectorAll(".converter").forEach(function (box) {
  var input = box.querySelector("#converter-in"), output = box.querySelector("#converter-out");
  var status = box.querySelector(".converter__status"), timer, asked = 0;
  function font() {
    var f = box.querySelector("input[name=converter-font]:checked");
    return f ? f.value : "";
  }
  function convert() {
    var text = input.value, ask = ++asked;
    if (!text) { output.value = ""; status.textContent = ""; return; }
    var data = new URLSearchParams({ input_text: text });
    if (font()) data.append("type", font());
    fetch(box.getAttribute("data-api"), { method: "POST", body: data })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (ask !== asked) return;
        output.value = d.unicode || "";
        status.textContent = "";
      })
      .catch(function () { status.textContent = "The converter could not be reached. Please try again later."; });
  }
  function later() { clearTimeout(timer); timer = setTimeout(convert, 300); }
  input.addEventListener("input", later);
  box.querySelectorAll("input[name=converter-font]").forEach(function (r) { r.addEventListener("change", convert); });
  box.querySelector(".converter__copy").addEventListener("click", function () {
    if (!output.value) { status.textContent = "There is nothing to copy yet. Paste your text in the first box."; return; }
    output.select();
    var done = function () { status.textContent = "Copied."; };
    if (navigator.clipboard) navigator.clipboard.writeText(output.value).then(done);
    else { document.execCommand("copy"); done(); }
  });
  box.querySelector(".converter__clear").addEventListener("click", function () {
    input.value = ""; output.value = ""; status.textContent = ""; input.focus();
  });
});
