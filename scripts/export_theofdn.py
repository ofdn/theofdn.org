#!/usr/bin/env python3
"""Export theofdn.org from WordPress into Markdown and local media.

Reads ../../site-audit/tiers.csv (tier and section per URL).
Writes:
  raw/wp/*.json        API responses, fetched once (--refresh to fetch again)
  content/<section>/   one Markdown file per page, with front matter
  assets/media/        every file from the media library, plus resized
                       copies that pages link to directly
  data/redirects.json  old path -> new path
  qa/alt-text-todo.csv images with no alt text
  qa/links-todo.csv    links that could not be resolved

Stops if content/ already exists, so hand edits are not overwritten.
--force overwrites content/. --refresh fetches from WordPress again.
"""
import csv, json, re, subprocess, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup

BASE = "https://theofdn.org"
ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT.parent / "site-audit"
RAW = ROOT / "raw" / "wp"
MEDIA = ROOT / "assets" / "media"
S = requests.Session()
S.headers["User-Agent"] = "OFDN-migration/1.0 (https://theofdn.org)"
REFRESH = "--refresh" in sys.argv

# Old paths linked inside posts that do not resolve on their own.
DEAD_LINK_TARGETS = {
    "/pothi": "/activities/pothi/",
    "/activities/mcc": "/activities/marginalized-community-council/",
    "/open-data-day-2018-bhubaneswar": "/blogs/conference/meetings/open-data-day-2018-bhubaneswar/",
    "/software-freedom-day-2017-bhubaneswar": "/blogs/software-freedom-day-2017-bhubaneswar/",
    "/wikimania2017": "/blogs/conference/wikimania2017/",
    "/category/tools/language-tool": "/category/openspeaks/language-resources/",
    "/globalvoices.org": "https://globalvoices.org/",
    "/openspeaks.com": "https://openspeaks.com/",
}
# Standalone tools on the server, outside WordPress. Copied as they are.
STATIC_TOOLS = {"suc": ["index.html", "script.js", "Shuttleworth Funded.jpg"]}

COMMONS_THUMB = re.compile(r"upload\.wikimedia\.org/wikipedia/commons/(?:thumb/)?\w/\w\w/([^/]+)(?:/(\d+)px-[^/]+)?$")


def commons_source(url):
    """Old Commons thumbnail sizes now return 400; ask FilePath for a width."""
    m = COMMONS_THUMB.search(url.split("?")[0])
    if not m:
        return url
    width = m.group(2) or "1280"
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{m.group(1)}?width={width}"


REDIRECT_TO = {"/podcast-3/": "/podcast/", "/activities/podcasts/": "/podcast/"}


def get(url, **kw):
    for i in range(3):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code < 500:
                return r
        except requests.RequestException:
            pass
        time.sleep(2 * (i + 1))
    return None


def fetch_all(rest_base):
    cache = RAW / f"{rest_base}.json"
    if cache.exists() and not REFRESH:
        return json.loads(cache.read_text())
    items, page = [], 1
    while True:
        r = get(f"{BASE}/wp-json/wp/v2/{rest_base}?per_page=100&page={page}")
        if r is None or r.status_code != 200 or not r.json():
            break
        items += r.json()
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
    cache.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    return items


def path_of(url):
    p = urlparse(url).path or "/"
    return p if p.endswith("/") or "." in p.rsplit("/", 1)[-1] else p + "/"


def local_media_path(url):
    """uploads/2019/08/file.jpg -> assets/media/2019/08/file.jpg"""
    u = urlparse(url)
    p = unquote(u.path)
    if not u.netloc.endswith("theofdn.org"):
        return MEDIA / "external" / u.netloc / p.lstrip("/") if u.netloc else None
    if "/wp-content/uploads/" not in p:
        return None
    return MEDIA / p.split("/wp-content/uploads/", 1)[1]


def download(url, dest):
    if dest.exists() and dest.stat().st_size:
        return True
    r = get(url)
    if r is None or r.status_code != 200:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    return True


def site_url(dest):
    return "/" + str(dest.relative_to(ROOT))


VIDEO_PATTERNS = [
    ("archive", re.compile(r"archive\.org/(?:embed|details)/([^/?#\"']+)")),
    ("soundcloud", re.compile(r"api\.soundcloud\.com/((?:tracks|playlists)/\d+)")),
    ("facebook", re.compile(r"facebook\.com/plugins/video\.php\?href=([^&]+)")),
    ("youtube", re.compile(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|v/)|youtu\.be/)([\w-]{11})")),
    ("vimeo", re.compile(r"vimeo\.com/(?:video/)?(\d+)")),
    ("commons", re.compile(r"commons\.wikimedia\.org/wiki/(File:[^?#\"']+)")),
]


def match_video(src):
    src = unquote(src or "")
    for provider, pat in VIDEO_PATTERNS:
        m = pat.search(src)
        if m:
            return {"provider": provider, "id": unquote(m.group(1))}
    return None


def clean_html(html, page_url, known_paths, alias_map, report):
    soup = BeautifulSoup(html, "html.parser")
    videos = []

    # Video embeds become markers; the build renders a click-to-play player.
    for tag in soup.find_all(["iframe", "video", "audio", "embed", "object"]):
        src = tag.get("src") or tag.get("data-src") or ""
        if not src and tag.get("data-mwtitle"):  # copied MediaWiki player
            src = "https://commons.wikimedia.org/wiki/File:" + tag["data-mwtitle"]
        if not src and tag.find("source"):
            src = tag.find("source").get("src", "")
        v = match_video(src)
        if not v and src and "/wp-content/uploads/" in src:
            dest = local_media_path(src)
            if download(src, dest):
                v = {"provider": "file", "id": site_url(dest)}
        if not v and re.search(r"\.(mp4|webm|ogv|mp3|ogg|oga|wav)(\?|$)", src, re.I):
            v = {"provider": "file", "id": src}
        if not v and src:
            # Forms, sheets and other embeds: kept as a titled link.
            v = {"provider": "link", "id": src, "title": tag.get("title", "")}
        if v:
            videos.append(v)
            marker = soup.new_tag("p")
            marker.string = f"[[embed:{len(videos) - 1}]]"
            (tag.find_parent("figure") or tag).replace_with(marker)
        else:
            tag.decompose()

    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()

    # Images: local copies, keep the original file where the library has it.
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        src = urljoin(BASE, src)
        for a in ("srcset", "sizes", "data-src", "data-srcset", "loading", "decoding", "class", "style", "width", "height"):
            img.attrs.pop(a, None)
        dest = local_media_path(src)
        if "i1.wp.com/" in src or "i0.wp.com/" in src or "i2.wp.com/" in src:
            src = "https://" + re.sub(r"^https?://i\d\.wp\.com/", "", src).split("?")[0]
            dest = local_media_path(src)
        if dest and "/external/" in str(dest):
            if download(commons_source(src), dest):
                img["src"] = site_url(dest)
            else:
                report["links"].append((page_url, src, "external image unreachable, kept remote"))
        elif dest:
            original = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", src)
            odest = local_media_path(original)
            if odest.exists() or download(original, odest):
                dest = odest
            elif not download(src, dest):
                report["links"].append((page_url, src, "image download failed"))
                continue
            img["src"] = site_url(dest)
        if not (img.get("alt") or "").strip():
            report["alt"].append((page_url, img.get("src", "")))

    # Links: media to local files, internal pages to clean paths.
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full = urljoin(BASE, href)
        u = urlparse(full)
        if not u.netloc.endswith("theofdn.org"):
            continue
        if "/wp-content/uploads/" in u.path:
            dest = local_media_path(full)
            if download(full.split("#")[0], dest):
                a["href"] = site_url(dest)
            else:
                report["links"].append((page_url, href, "file download failed"))
            continue
        path = path_of(full)
        key = path.rstrip("/")
        frag = f"#{u.fragment}" if u.fragment else ""
        if key in DEAD_LINK_TARGETS:
            a["href"] = DEAD_LINK_TARGETS[key]
        elif path in known_paths or path.startswith("/category/") or path.startswith("/tag/"):
            a["href"] = REDIRECT_TO.get(path, path) + frag
        elif key in alias_map:
            a["href"] = alias_map[key] + frag
        else:
            report["links"].append((page_url, href, "unknown internal path"))

    # Layout tables (cells holding images, lists or several paragraphs)
    # become plain paragraphs; data tables stay tables.
    for table in soup.find_all("table"):
        cells = table.find_all(["td", "th"])
        layout = any(c.find(["img", "ul", "ol", "h1", "h2", "h3", "h4", "table"]) or len(c.find_all("p")) > 1
                     for c in cells)
        if layout:
            frag = soup.new_tag("div")
            for c in cells:
                if c.get_text(strip=True) or c.find("img"):
                    block = soup.new_tag("p") if not c.find(["p", "ul", "ol", "h2", "h3", "h4", "img"]) else soup.new_tag("div")
                    block.extend(list(c.contents))
                    frag.append(block)
            table.replace_with(frag)
        else:
            for br in table.find_all("br"):
                br.replace_with("; ")
            for p_ in table.find_all("p"):
                p_.unwrap()
    # Side-by-side label/value tables (two colspan=2 headers over four
    # columns) become two plain tables, one per header.
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        head = rows[0].find_all(["td", "th"]) if rows else []
        def logical(r):
            cols = []
            for c in r.find_all(["td", "th"]):
                cols += [c] * int(c.get("colspan") or 1)
            return cols
        if len(head) == 2 and all(h.get("colspan") == "2" for h in head) and \
                all(len(logical(r)) == 4 for r in rows[1:]):
            frag = soup.new_tag("div")
            for side in (0, 1):
                h = soup.new_tag("h3"); h.string = head[side].get_text(" ", strip=True)
                t = soup.new_tag("table")
                hr = soup.new_tag("tr")
                for label in ("Field", "Value"):
                    th = soup.new_tag("th"); th.string = label; hr.append(th)
                t.append(hr)
                for r in rows[1:]:
                    c = logical(r)[side * 2: side * 2 + 2]
                    if not any(x.get_text(strip=True) for x in c):
                        continue
                    tr = soup.new_tag("tr")
                    if c[0] is c[1]:  # sub-heading across both columns
                        td = soup.new_tag("td"); b = soup.new_tag("strong")
                        b.string = c[0].get_text(" ", strip=True); td.append(b); tr.append(td)
                        tr.append(soup.new_tag("td"))
                    else:
                        for x in c:
                            td = soup.new_tag("td"); td.extend(list(x.contents)); tr.append(td)
                    t.append(tr)
                frag.extend([h, t])
            table.replace_with(frag)
    for tag in soup.find_all(["colgroup", "col"]):
        tag.decompose()

    # Page-builder wrappers carry no meaning once styling is gone.
    for fig in soup.find_all("figure"):
        cap = fig.find("figcaption")
        if cap:
            cap.name = "p"
            em = soup.new_tag("em")
            em.extend(list(cap.contents))
            cap.append(em)
        fig.unwrap()
    for tag in soup.find_all(["div", "span", "section", "font", "center", "small", "u"]):
        tag.unwrap()
    keep = {"a": {"href", "title"}, "img": {"src", "alt", "title"},
            "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"}}
    for tag in soup.find_all(True):
        allowed = keep.get(tag.name, set())
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
    # Keep images with an empty alt from being linked to themselves only.
    for a in soup.find_all("a"):
        if not a.get_text(strip=True) and not a.find("img"):
            a.unwrap()
    return str(soup), videos


def to_markdown(html):
    r = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"],
                       input=html, capture_output=True, text=True, check=True)
    md = r.stdout
    md = re.sub(r"\\\[\\\[embed:(\d+)\\\]\\\]", r"[[embed:\1]]", md)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def yaml_str(v):
    return json.dumps(v, ensure_ascii=False)


def to_yaml(front):
    """Plain YAML, one field per line, lists as indented items."""
    out = []
    for k, v in front.items():
        if v in (None, [], ""):
            continue
        if isinstance(v, list):
            out.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    pairs = [(a, b) for a, b in item.items() if b not in (None, "")]
                    out.append(f"  - {pairs[0][0]}: {yaml_str(pairs[0][1])}")
                    out += [f"    {a}: {yaml_str(b)}" for a, b in pairs[1:]]
                else:
                    out.append(f"  - {yaml_str(item)}")
        elif isinstance(v, int):
            out.append(f"{k}: {v}")
        else:
            out.append(f"{k}: {yaml_str(v)}")
    return out


def text_of(html):
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def main():
    if (ROOT / "content").exists() and "--force" not in sys.argv:
        sys.exit("content/ exists and may have hand edits. Use --force to overwrite it.")
    for d in (RAW, MEDIA, ROOT / "content", ROOT / "data", ROOT / "qa"):
        d.mkdir(parents=True, exist_ok=True)

    tiers = {path_of(r["url"]): r for r in csv.DictReader(open(AUDIT / "tiers.csv"))}
    inventory = json.loads((AUDIT / "inventory.json").read_text())
    alias_map = {}
    for old, (status, final) in inventory["linked_not_in_api"].items():
        if status == 200 and final:
            alias_map[path_of(old).rstrip("/")] = path_of(final)

    posts, pages, media = fetch_all("posts"), fetch_all("pages"), fetch_all("media")
    cats = {c["id"]: c for c in fetch_all("categories")}
    tags = {t["id"]: t["name"] for t in fetch_all("tags")}
    authors = {u["id"]: u["name"] for u in fetch_all("users")}

    # Whole media library, so nothing is lost when WordPress goes offline.
    failed = 0
    for m in media:
        dest = local_media_path(m["source_url"])
        if dest and not download(m["source_url"], dest):
            failed += 1
    print(f"media: {len(media)} in library, {failed} failed", file=sys.stderr)

    for tool, files in STATIC_TOOLS.items():
        for f in files:
            if not download(f"{BASE}/{tool}/" + ("" if f == "index.html" else f), ROOT / "tools" / tool / f):
                print(f"tool file failed: {tool}/{f}", file=sys.stderr)

    known = {path_of(it["link"]) for it in posts + pages}
    known |= {f"/{t}/" for t in STATIC_TOOLS}
    report = {"alt": [], "links": []}
    redirects = dict(REDIRECT_TO)
    redirects.update({k + "/": v for k, v in alias_map.items()})
    redirects.update({k + "/": v for k, v in DEAD_LINK_TARGETS.items() if v.startswith("/")})
    written = 0

    for it in posts + pages:
        path = path_of(it["link"])
        row = tiers.get(path)
        if row is None:
            print(f"not in tiers.csv, skipped: {path}", file=sys.stderr)
            continue
        if row["tier"] in ("drop", "redirect"):
            continue
        html, videos = clean_html(it["content"]["rendered"], path, known, alias_map, report)
        body = to_markdown(html)
        featured = None
        if it.get("featured_media"):
            fm = next((m for m in media if m["id"] == it["featured_media"]), None)
            if fm and local_media_path(fm["source_url"]):
                featured = site_url(local_media_path(fm["source_url"]))
        front = {
            "title": text_of(it["title"]["rendered"]),
            "path": path,
            "tier": row["tier"],
            "section": row["section"],
            "wp_type": it["type"],
            "wp_id": it["id"],
            "date": it["date"][:10],
            "modified": it["modified"][:10],
            "author": authors.get(it.get("author")),
            "categories": [cats[c]["name"] for c in it.get("categories", []) if c in cats],
            "tags": [tags.get(t) for t in it.get("tags", []) if t in tags],
            "excerpt": text_of(it.get("excerpt", {}).get("rendered", "")),
            "featured_image": featured,
            "embeds": videos,
            "original_url": it["link"],
        }
        lines = ["---"] + to_yaml(front) + ["---", ""]
        slug = "index" if path == "/" else path.strip("/").rsplit("/", 1)[-1]
        out = ROOT / "content" / row["section"] / f"{slug}.md"
        if out.exists():
            out = out.with_name(path.strip("/").replace("/", "-") + ".md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + body)
        written += 1

    (ROOT / "data" / "redirects.json").write_text(json.dumps(dict(sorted(redirects.items())), indent=1))
    with open(ROOT / "qa" / "alt-text-todo.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["page", "image", "alt"]); w.writerows(r + ("",) for r in report["alt"])
    with open(ROOT / "qa" / "links-todo.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["page", "link", "problem"]); w.writerows(report["links"])
    print(f"pages written: {written}, redirects: {len(redirects)}, images without alt: {len(report['alt'])}, "
          f"link problems: {len(report['links'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
