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
document.querySelectorAll(".copy-btn[data-copy], .citation-copy").forEach(function (btn) {
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
