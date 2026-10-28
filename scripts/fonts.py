#!/usr/bin/env python3
"""python3 scripts/fonts.py <name> <export>

Needs hb-shape (HarfBuzz) and the Python packages fonttools and brotli.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import WOFF2FlavorData
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import CONJUNCT, SITE_URL, font_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOTICE = ("This font software contains a limited selection of production glyphs, furnished solely for "
          "purposes of display. Said glyphs do not constitute a release and are not released for public use.")


def texts_for(name):
    texts, face = [], {}
    for f in (ROOT / "content").rglob("*.md"):
        body = f.read_text()
        for m in re.finditer(r'<(specimen|inuse)\b([^>]*)>(.*?)</\1>', body, re.S):
            if re.search(rf'font="{re.escape(name)}"', m.group(2)):
                text = m.group(3)
                if m.group(1) == "inuse":  # drop the book:/sign:/screen: keys
                    text = re.sub(r"^\s*\w+:\s*", "", text, flags=re.M)
                texts.append(text)
        for m in re.finditer(r'<typeface>(.*?)</typeface>', body, re.S):
            t = yaml.safe_load(m.group(1)) or {}
            if t.get("font") == name:
                src = t.get("source") or {}
                for v in [t.get("display", ""), t.get("headline", ""), t.get("text", "")] + (t.get("words") or []) + (src.get("lines") or []):
                    texts.append(str(v))
                face = t
    return texts, face


def runs(texts):
    whole = "".join(texts)
    out = {w for t in texts for w in t.split()}
    out |= {c for c in whole if not c.isspace()}
    out |= {"କ" + c for c in whole if "଀" <= c <= "୿"}
    out |= set(CONJUNCT.findall(whole))
    return sorted(out)


def shaped(font, text):
    p = subprocess.run(["hb-shape", "--trace", "--no-clusters", "--no-positions", str(font), text],
                       capture_output=True, text=True, check=True)
    names = set()
    for b in re.findall(r"buffer: \[([^\]]*)\]", p.stdout + p.stderr):
        names |= set(b.split("|"))
    return names - {""}


def final(font, text):
    return subprocess.run(["hb-shape", "--no-clusters", str(font), text],
                          capture_output=True, text=True, check=True).stdout


def mark(font, face, source, stem):
    names = font["name"]
    style = names.getDebugName(2) or "Regular"
    version = (names.getDebugName(5) or "").replace("Version ", "")
    cut = hashlib.sha1(Path(source).read_bytes()).hexdigest()[:10]
    designer = (face.get("credits") or {}).get("designer", "")
    credits = [("Designer", n.strip()) for n in str(designer).split(",") if n.strip()]
    for i in (13, 14, 19):
        names.removeNames(nameID=i)
    fields = {1: stem, 16: stem, 4: f"{stem} {style}", 6: f"{stem}-{style}", 3: f"{version};ofdn;{cut}",
              5: f"Version {version}; {cut}", 8: "O Foundation", 11: SITE_URL, 10: NOTICE}
    designers = [n for r, n in credits if r == "Designer"]
    if designers:
        fields[9] = ", ".join(designers)
    for i, text in fields.items():
        names.setName(text, i, 3, 1, 0x409)
        if names.getName(i, 1, 0, 0):
            names.setName(text, i, 1, 0, 0)
    meta = (f'<?xml version="1.0" encoding="UTF-8"?>\n<metadata version="1.0">\n'
            f'  <uniqueid id="org.theofdn.{stem}.{cut}"/>\n'
            f'  <vendor name="O Foundation" url="{SITE_URL}"/>\n  <credits>\n'
            + "".join(f'    <credit name="{escape(n)}" role="{escape(r)}"/>\n' for r, n in credits)
            + f'  </credits>\n  <description>\n    <text xml:lang="en">{escape(NOTICE)}</text>\n'
            f'  </description>\n</metadata>\n')
    font.flavorData = WOFF2FlavorData()
    font.flavorData.metaData = meta.encode()


def metrics(font):
    """Ascender, descender, the height of the consonants and the highest and
    lowest points of the glyphs, in font units."""
    os2, glyphs, cmap = font["OS/2"], font.getGlyphSet(), font.getBestCmap()
    bounds = []
    for name in font.getGlyphOrder():
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        if pen.bounds:
            bounds.append(pen.bounds)
    tops = []
    for c in range(0x0B15, 0x0B3A):
        if c in cmap:
            pen = BoundsPen(glyphs)
            glyphs[cmap[c]].draw(pen)
            if pen.bounds:
                tops.append(pen.bounds[3])
    return {"upm": font["head"].unitsPerEm, "ascender": os2.sTypoAscender, "descender": os2.sTypoDescender,
            "top": round(max(b[3] for b in bounds)), "bottom": round(min(b[1] for b in bounds)),
            "letter": round(sorted(tops)[len(tops) // 2]) if tops else os2.sxHeight,
            "weight": os2.usWeightClass, "style": font["name"].getDebugName(2) or "Regular"}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    name, source = sys.argv[1], Path(sys.argv[2]).expanduser()
    texts, face = texts_for(name)
    if not texts:
        sys.exit(f"No <specimen>, <inuse> or <typeface> block uses font=\"{name}\".")
    words = runs(texts)
    keep = set()
    for w in words:
        keep |= shaped(source, w)
    font = TTFont(source)
    stem = font_file(name)
    out = ROOT / "assets" / "fonts" / f"{stem}.woff2"
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.layout_closure = False
    opts.name_IDs = ["*"]
    opts.glyph_names = True
    sub = subset.Subsetter(opts)
    sub.populate(glyphs=sorted(keep), text="".join(texts))
    sub.subset(font)
    with tempfile.NamedTemporaryFile(suffix=".ttf") as check:
        font.save(check.name)
        wrong = [w for w in words if final(source, w) != final(check.name, w)]
    if wrong:
        sys.exit(f"Shaped differently: {' '.join(wrong)}")
    font["post"].formatType = 3.0
    out.with_suffix(".json").write_text(json.dumps(metrics(font)) + "\n")
    font.flavor = "woff2"
    mark(font, face, source, stem)
    font.save(out)
    print(f"{out.relative_to(ROOT)}: {len(font.getGlyphOrder())} glyphs, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
