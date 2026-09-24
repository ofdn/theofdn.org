#!/usr/bin/env python3
"""Build the site from content/ into _site/.

  python3 scripts/build.py                     for theofdn.org
  python3 scripts/build.py --base /theofdn.org for ofdn.github.io/theofdn.org

Needs pandoc, and the Python packages pyyaml, jinja2 and beautifulsoup4.
"""
import argparse, json, re, shutil, subprocess, sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
SITE_NAME = "O Foundation"
SITE_URL = "https://theofdn.org"

# Header navigation. Contact, donate and policies sit in the footer.
NAV = [
    ("Films", "/category/film/"),
    ("Podcast", "/podcast/"),
    ("Resources", "/category/oer/"),
    ("OpenSpeaks", "/openspeaks/"),
    ("Initiatives", "/work/"),
    ("Publications", "/category/blogs/"),
    ("About", "/people/"),
]
FOOTER_NAV = [
    ("About", [("People", "/people/"), ("Partners and advisors", "/partners/"), ("Core values", "/core/"),
               ("Diversity and inclusion", "/diversity-and-inclusion/"), ("Contact", "/reach-out/")]),
    ("Work", [("Films", "/category/film/"), ("Podcast", "/podcast/"), ("Resources", "/category/oer/"),
              ("OpenSpeaks", "/openspeaks/"), ("Initiatives", "/work/"), ("Publications", "/category/blogs/")]),
    ("Policies", [("Site policies", "/policies/"), ("Licensing", "/licensing/"), ("Issues", "/issues/"),
                  ("Donate", "/donate/")]),
    ("Follow", [("YouTube", "https://www.youtube.com/channel/UCk4NuEPO6JbTm_8Ybod2eOQ"),
                ("Instagram", "https://instagram.com/ofdnorg/"), ("Facebook", "https://facebook.com/theofdn/"),
                ("X (Twitter)", "https://twitter.com/ofdnorg/"), ("GitHub", "https://github.com/ofdn")]),
]

# Listing pages, kept at the old WordPress category addresses.
LISTS = {
    "/category/film/": ("Films", ["film"], "Documentary films by O Foundation."),
    "/category/oer/": ("Resources", ["oer", "tool", "audio-archive"],
                       "Open educational resources, language tools and toolkits."),
    "/category/openspeaks/language-resources/": ("Language tools", ["tool"], "Language tools and toolkits."),
    "/category/blogs/": ("Publications", ["blog", "archive"], "Blog posts, reports and older pages kept as a record."),
}
EYEBROW = {
    "film": "Documentary film", "podcast": "Podcast", "oer": "Open educational resource",
    "tool": "Language tool", "audio-archive": "Audio archive", "archive": "Archive", "blog": "Blog",
}
TEMPLATE = {"film": "film.html", "podcast": "film.html", "oer": "module.html", "tool": "module.html",
            "audio-archive": "module.html", "archive": "page.html", "blog": "page.html", "hub": "page.html", "about": "page.html"}

# Links in the details column of film and podcast pages. The address decides
# the label and the icon (templates/icons, Simple Icons, CC0).
LINK_TYPES = [
    ("imdb.com", "IMDb", "imdb"), ("doi.org", "DOI", "doi"), ("eidr.org", "EIDR", "link"),
    ("archive.org", "Internet Archive", "internetarchive"), ("wikidata.org", "Wikidata", "wikidata"),
    ("letterboxd.com", "Letterboxd", "letterboxd"), ("moviebuff.com", "Moviebuff", "link"),
    ("loc.gov", "Library of Congress", "link"), ("youtube.com", "YouTube", "youtube"),
    ("vimeo.com", "Vimeo", "vimeo"), ("spotify.com", "Spotify", "spotify"),
    ("podcasts.apple.com", "Apple Podcasts", "applepodcasts"), ("soundcloud.com", "SoundCloud", "soundcloud"),
]
STATUSES = ("live", "maintenance", "archive")
STATUS_TEXT = {
    "site": {"archive": "This website has been archived. It is kept as a record and is no longer updated.",
             "maintenance": "This website is being updated. Please come back in a little while."},
    "page": {"archive": "This page has been archived. It is kept as a record and is no longer updated.",
             "maintenance": "This page is being updated. Please come back in a little while."},
}

# Scripts that get a lang attribute when a block is written in them.
SCRIPTS = [("sat-Olck", "᱐", "᱿"), ("or", "଀", "୿"), ("hoc-Wara", "\U000118a0", "\U000118ff")]


def load_pages():
    pages = []
    for f in sorted((ROOT / "content").rglob("*.md")):
        text = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            sys.exit(f"{f}: missing the block between --- lines at the top")
        meta = yaml.safe_load(m.group(1)) or {}
        meta["body_md"] = m.group(2)
        meta["file"] = f.relative_to(ROOT).as_posix()
        for key in ("title", "path", "section"):
            if not meta.get(key):
                sys.exit(f"{f}: missing '{key}'")
        meta["date"] = str(meta.get("date", ""))
        if not re.fullmatch(r"/([a-z0-9-]+/)*", meta["path"]):
            sys.exit(f"{f}: path '{meta['path']}' must start and end with / and use only a-z, 0-9 and -")
        pages.append(meta)
    seen = {}
    for p in pages:
        if p["path"] in seen:
            sys.exit(f"{p['file']} and {seen[p['path']]} have the same path {p['path']}")
        seen[p["path"]] = p["file"]
    return pages


def markdown_to_html(md):
    r = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
                       input=md, capture_output=True, text=True, check=True)
    return r.stdout


def embed_html(e, title, section):
    p, i = e.get("provider"), str(e.get("id", ""))
    label = e.get("title") or title
    if p == "youtube":
        return (f'<div class="embed-video embed-video--large"><a class="embed-play" href="https://www.youtube.com/watch?v={i}" '
                f'data-embed="https://www.youtube-nocookie.com/embed/{i}?autoplay=1&amp;rel=0" data-title="{label}">'
                f'<img src="https://i.ytimg.com/vi/{i}/hqdefault.jpg" alt="" loading="lazy">'
                f'<span class="embed-play__button">Play video<span class="visually-hidden">: {label}</span></span></a></div>')
    if p == "vimeo":
        return (f'<div class="embed-video embed-video--large"><iframe src="https://player.vimeo.com/video/{i}" '
                f'title="{label}" loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>')
    if p == "archive":
        cls = "embed-audio" if section == "podcast" or e.get("audio") else "embed-video embed-video--large"
        return (f'<div class="{cls}"><iframe src="https://archive.org/embed/{i}" title="{label}" '
                f'loading="lazy" allowfullscreen></iframe></div>')
    if p == "soundcloud":
        h = 450 if i.startswith("playlists") else 166
        src = "https://w.soundcloud.com/player/?url=" + quote(f"https://api.soundcloud.com/{i}", safe="")
        return f'<div class="embed-audio" style="height:{h}px"><iframe src="{src}" title="{label}" loading="lazy"></iframe></div>'
    if p == "commons":
        name = i.split(":", 1)[-1]
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(name)
        page = "https://commons.wikimedia.org/wiki/" + quote(i)
        return media_tag(url, page, name)
    if p == "file":
        return media_tag(i, i, i.rsplit("/", 1)[-1])
    if p == "tool":
        return (f'<div class="embed-tool"><iframe src="{i}" title="{label}" loading="lazy"></iframe></div>'
                f'<p class="embed-link"><a href="{i}">Open {label} in its own page</a></p>')
    if p == "facebook":
        return f'<p class="embed-link"><a href="{i}">Watch the video on Facebook</a></p>'
    host = re.sub(r"^https?://(www\.)?", "", i).split("/")[0]
    return f'<p class="embed-link"><a href="{i}">{e.get("title") or "Open the embedded content"}</a> ({host})</p>'


def media_tag(url, page, name):
    ext = name.rsplit(".", 1)[-1].lower()
    if ext in ("wav", "ogg", "oga", "mp3", "flac", "opus", "m4a"):
        return (f'<figure class="embed-file"><audio controls preload="none" src="{url}"></audio>'
                f'<figcaption><a href="{page}">{name}</a></figcaption></figure>')
    if ext in ("webm", "ogv", "mp4"):
        return (f'<figure class="embed-file"><video controls preload="none" src="{url}"></video>'
                f'<figcaption><a href="{page}">{name}</a></figcaption></figure>')
    return f'<p class="embed-link"><a href="{page}">{name}</a></p>'


def fallback_of(src):
    for ext in (".fallback.jpg", ".fallback.png"):
        f = ROOT / (src.lstrip("/").rsplit(".", 1)[0] + ext)
        if f.exists():
            return "/" + f.relative_to(ROOT).as_posix()
    return None


def picture(src, alt="", cls="", portrait=None, lazy=True):
    """An image as WebP with its small fallback; optional portrait version for phones."""
    if not src:
        return ""
    from markupsafe import Markup, escape
    fb = fallback_of(src) or src
    parts = ["<picture>"]
    if portrait:
        parts.append(f'<source media="(max-width: 700px)" srcset="{portrait}" type="image/webp">')
    parts.append(f'<source srcset="{src}" type="image/webp">')
    attrs = f' class="{cls}"' if cls else ""
    load = ' loading="lazy"' if lazy else ""
    parts.append(f'<img src="{fb}" alt="{escape(alt)}"{attrs}{load} decoding="async"></picture>')
    return Markup("".join(parts))


def inline_md(text):
    """Links, bold and italics in short values such as datasheet lines."""
    from markupsafe import Markup, escape
    t = str(escape(str(text)))
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = t.replace("\\|", "|").replace("\\", "")
    return Markup(t)


def link_item(entry):
    """A 'links' entry is an address, or a label and url pair."""
    url = entry if isinstance(entry, str) else entry["url"]
    label, icon = None, "link"
    for host, name, ic in LINK_TYPES:
        if host in url:
            label, icon = name, ic
            break
    if not isinstance(entry, str) and entry.get("label"):
        label = entry["label"]
    if not label:
        label = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    detail = None
    m = re.search(r"(10\.\d{4,}/[^\s?#]+)", url)
    if icon == "doi" or label == "EIDR":
        detail = m.group(1) if m else None
    return {"url": url, "label": label, "icon": icon, "detail": detail}


def load_status():
    f = ROOT / "data" / "site.yml"
    conf = yaml.safe_load(f.read_text()) if f.exists() else {}
    conf = conf or {}
    if conf.get("status", "live") not in STATUSES:
        sys.exit(f"data/site.yml: status must be one of {', '.join(STATUSES)}")
    return conf


def page_status(page, conf):
    """The page's own status wins over the site status."""
    own = page.get("status") if page else None
    if own and own not in STATUSES:
        sys.exit(f"{page['file']}: status must be one of {', '.join(STATUSES)}")
    if own and own != "live":
        return {"kind": own, "text": page.get("status_message") or STATUS_TEXT["page"][own]}
    kind = conf.get("status", "live")
    if kind == "live":
        return None
    return {"kind": kind, "text": conf.get(f"{kind}_message") or STATUS_TEXT["site"][kind]}


def script_lang(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return None
    for code, lo, hi in SCRIPTS:
        if sum(lo <= c <= hi for c in letters) / len(letters) > 0.5:
            return code
    return None


def polish(html, page):
    soup = BeautifulSoup(html, "html.parser")
    embeds = page.get("embeds") or []

    for p in soup.find_all("p"):
        m = re.fullmatch(r"\s*\[\[embed:(\d+)\]\]\s*", p.get_text())
        if m:
            n = int(m.group(1))
            new = embed_html(embeds[n], page["title"], page["section"]) if n < len(embeds) else ""
            p.replace_with(BeautifulSoup(new, "html.parser"))

    # WebP with a small fallback for browsers that cannot show WebP.
    for img in soup.find_all("img"):
        src = img.get("src", "")
        img["loading"] = "lazy"
        img["decoding"] = "async"
        if img.find_parent("a", class_="embed-play"):
            continue
        fb = fallback_of(src) if src.startswith("/assets/") and src.endswith(".webp") else None
        if fb:
            picture = soup.new_tag("picture")
            source = soup.new_tag("source", srcset=src, type="image/webp")
            img.replace_with(picture)
            img["src"] = fb
            picture.append(source)
            picture.append(img)

    # Heading levels in order: the page title is h1, body headings follow.
    heads = soup.find_all(re.compile(r"^h[1-6]$"))
    levels = sorted({int(h.name[1]) for h in heads})
    remap = {lvl: min(i + 2, 6) for i, lvl in enumerate(levels)}
    for h in heads:
        h.name = f"h{remap[int(h.name[1])]}"
        if not h.get_text(strip=True) and not h.find("img"):
            h.unwrap()

    # Quotes: every blockquote gets the same look. The last paragraph that
    # starts with a dash is the attribution. Runs of quotes form a grid.
    for bq in soup.find_all("blockquote"):
        paras = bq.find_all("p", recursive=False)
        fig = soup.new_tag("figure", attrs={"class": "quote"})
        bq.wrap(fig)
        if paras and re.match(r"^\s*[—–]", paras[-1].get_text()):
            cap = soup.new_tag("figcaption")
            last = paras[-1]
            first = last.contents[0] if last.contents else None
            if isinstance(first, str):
                first.replace_with(re.sub(r"^\s*[—–]\s*", "", first))
            cap.extend(list(last.contents))
            last.decompose()
            fig.append(cap)
        for p_ in bq.find_all("p", recursive=False):
            text = p_.get_text()
            if re.match(r"^[★☆]", text):
                # Stars for the eye; the words for screen readers.
                stars = re.match(r"^[★☆]+", text).group(0)
                p_.clear()
                p_["class"] = "quote__rating"
                shown = soup.new_tag("span", attrs={"aria-hidden": "true"})
                shown.string = stars
                said = soup.new_tag("span", attrs={"class": "visually-hidden"})
                said.string = f"Rated {stars.count('★')} out of {len(stars)}"
                p_.extend([shown, said])
    for fig in soup.find_all("figure", class_="quote"):
        if fig.find_parent("div", class_="quotes"):
            continue
        run = [fig]
        nxt = fig.find_next_sibling()
        while nxt is not None and nxt.name == "figure" and "quote" in (nxt.get("class") or []):
            run.append(nxt)
            nxt = nxt.find_next_sibling()
        if len(run) > 1:
            box = soup.new_tag("div", attrs={"class": "quotes"})
            fig.insert_before(box)
            for f in run:
                box.append(f.extract())

    # Jump links to a part of the same page that no longer exists become text.
    ids = {t.get("id") for t in soup.find_all(id=True)}
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("#") and len(a["href"]) > 1 and a["href"][1:] not in ids:
            a.unwrap()

    # Wide tables scroll inside their own box.
    for t in soup.find_all("table"):
        wrap = soup.new_tag("div", attrs={"class": "table-wrap", "role": "region", "tabindex": "0",
                                          "aria-label": "Table"})
        t.wrap(wrap)

    for tag in soup.find_all(["p", "li", "td", "th", "h2", "h3", "h4", "blockquote"]):
        lang = script_lang(tag.get_text())
        if lang and not tag.find_parent(attrs={"lang": True}):
            tag["lang"] = lang
    return str(soup)


def split_datasheet(html):
    """Film pages: move the 'Datasheet' section into the details column.
    It is either a table or pairs of paragraphs: a bold label, then its value."""
    soup = BeautifulSoup(html, "html.parser")
    h = next((x for x in soup.find_all(re.compile("^h[2-4]$")) if x.get_text(strip=True).lower() == "datasheet"), None)
    if not h:
        return html, []
    section = []
    for sib in h.find_next_siblings():
        if re.match(r"^h[1-4]$", sib.name or "") and int(sib.name[1]) <= int(h.name[1]):
            break
        section.append(sib)
    facts, label = [], None
    for el in section:
        table = el if el.name == "table" else el.find("table")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) == 2 and cells[0].get_text(strip=True):
                    facts.append((cells[0].get_text(" ", strip=True), cells[1].decode_contents()))
            continue
        strong = el.find("strong") if el.name == "p" else None
        if strong and el.get_text(strip=True) == strong.get_text(strip=True):
            label = strong.get_text(" ", strip=True)
        elif label and el.name == "p":
            facts.append((label, el.decode_contents()))
            label = None
    if not facts:
        return html, []
    h.decompose()
    for el in section:
        el.decompose()
    return str(soup), facts


def citations(page):
    authors = page.get("authors")
    if not authors:
        return None
    names = ", ".join(authors[:-1]) + (" and " if len(authors) > 1 else "") + authors[-1]
    year = page["date"][:4]
    url = SITE_URL + page["path"]
    title = page["title"]
    ark = f" ARK: {page['ark']}" if page.get("ark") else ""
    key = re.sub(r"[^a-z0-9]+", "", page["path"].lower())[:30] or "ofdn"
    return {
        "apa": f"{names} ({year}). {title}. O Foundation. {url}",
        "chicago": f"{names}. \"{title}.\" O Foundation, {year}. Accessed __ACCESSED__. {url}.",
        "mla": f"{names}. \"{title}.\" O Foundation, {year}, {url}. Accessed __ACCESSED__.",
        "vancouver": f"{names}. {title}. O Foundation; {year} [cited __ACCESSED__]. Available from: {url}",
        "bibtex": ("@misc{" + key + ",\n  author    = {" + " and ".join(authors) + "},\n  title     = {" + title
                   + "},\n  publisher = {O Foundation},\n  year      = {" + year + "},\n  url       = {" + url
                   + "},\n  urldate   = {__ACCESSED__}" + (",\n  note      = {" + ark.strip() + "}" if ark else "") + "\n}"),
    }


def with_base(html, base):
    if not base:
        return html
    return re.sub(r'(\s(?:href|src|srcset|data-embed|action)=")/(?!/)', rf"\1{base}/", html)


def summary(page):
    text = page.get("excerpt") or ""
    text = re.sub(r"\s*\[…\]\s*$", "…", text)
    return text[:220] + ("…" if len(text) > 220 and not text.endswith("…") else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="", help="path prefix, e.g. /theofdn.org")
    ap.add_argument("--out", default="_site")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    out = ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    shutil.copytree(ROOT / "assets", out / "assets")
    shutil.copytree(ROOT / "tools", out / "tools")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    pages = load_pages()
    by_section = {}
    for p in pages:
        by_section.setdefault(p["section"], []).append(p)
    for items in by_section.values():
        items.sort(key=lambda p: p["date"], reverse=True)
    conf = load_status()
    site_status = page_status(None, conf)
    import hashlib
    asset_v = hashlib.sha1((ROOT / "assets/site.css").read_bytes() + (ROOT / "assets/site.js").read_bytes()).hexdigest()[:8]
    common = {"asset_v": asset_v, "nav": NAV, "footer_nav": FOOTER_NAV, "site_name": SITE_NAME, "year": date.today().year}

    def write(path, html):
        dest = out / path.strip("/") / "index.html" if path != "/" else out / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(with_base(html, base))

    for p in pages:
        body = polish(markdown_to_html(p["body_md"]), p)
        facts = []
        if p.get("details"):
            facts = [(d["label"], "<br>".join(str(inline_md(v)) for v in d["value"])) for d in p["details"]]
        elif p["section"] == "film":
            body, facts = split_datasheet(body)
        if p.get("trailer"):
            p["trailer_html"] = embed_html(p["trailer"], p["title"] + ", trailer", p["section"])
        if p.get("transcript"):  # optional, for films and podcast episodes
            p["transcript_html"] = polish(markdown_to_html(str(p["transcript"])), p)
        p["links_list"] = [link_item(x) for x in p.get("links") or []]
        p["listen_list"] = [link_item(x) for x in p.get("listen") or []]
        tpl = "home.html" if p["path"] == "/" else TEMPLATE.get(p["section"], "page.html")
        cite = citations(p)
        html = env.get_template(tpl).render(
            page=p, body=body, facts=facts, eyebrow=EYEBROW.get(p["section"]),
            citation=json.dumps(cite, ensure_ascii=False) if cite else None,
            current=p["path"], lists=by_section, summary=summary, picture=picture,
            status=page_status(p, conf), **common)
        write(p["path"], html)

    for path, (title, sections, lede) in LISTS.items():
        items = [p for s in sections for p in by_section.get(s, [])]
        items.sort(key=lambda p: p["date"], reverse=True)
        html = env.get_template("list.html").render(
            title=title, lede=lede, items=items, summary=summary, current=path, status=site_status, **common)
        write(path, html)

    redirects = json.loads((ROOT / "data" / "redirects.json").read_text())
    for line in (ROOT / "data" / "legacy-urls.txt").read_text().split():
        redirects.setdefault(line, legacy_target(line))
    for old, new in redirects.items():
        target = new if new.startswith("http") else base + new
        dest = out / old.strip("/") / "index.html"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(env.get_template("redirect.html").render(target=target))

    (out / "404.html").write_text(with_base(env.get_template("404.html").render(current="", status=site_status, **common), base))
    (out / ".nojekyll").write_text("")
    urls = [SITE_URL + p["path"] for p in pages] + [SITE_URL + p for p in LISTS]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in sorted(urls)) + "</urlset>\n")
    print(f"built {len(pages)} pages, {len(LISTS)} lists, {len(redirects)} redirects into {args.out}/", file=sys.stderr)


def legacy_target(path):
    """Old WordPress category and tag pages go to the closest list."""
    if path.startswith("/category/film"):
        return "/category/film/"
    if path.startswith("/category/podcast"):
        return "/podcast/"
    if path.startswith("/category/openspeaks/language-resources"):
        return "/category/openspeaks/language-resources/"
    if path.startswith(("/category/oer", "/category/openspeaks")):
        return "/category/oer/"
    return "/category/blogs/"


if __name__ == "__main__":
    main()
