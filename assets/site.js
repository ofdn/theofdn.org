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
