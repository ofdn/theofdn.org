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
