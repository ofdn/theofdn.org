#!/usr/bin/env python3
"""Make the cut-down copy of an unreleased font for the website.

  python3 scripts/subset_fonts.py chapakala19 /path/to/Chapakala19Regular.woff2

Keeps only the characters that <specimen>, <inuse> and <typeface> blocks use
with this font, plus the conjuncts and shapes those characters need. Writes
assets/fonts/<name>.woff2, and assets/fonts/<name>.json with the metrics the
glyph inspector draws. Run it again after changing the sample text or
getting a new export. The full font stays outside this repository.

Needs the Python packages fonttools and brotli.
"""
import json
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
import yaml

ROOT = Path(__file__).resolve().parent.parent


def texts_for(name):
    chars = set()
    for f in (ROOT / "content").rglob("*.md"):
        body = f.read_text()
        for m in re.finditer(r'<(specimen|inuse)\b([^>]*)>(.*?)</\1>', body, re.S):
            if re.search(rf'font="{re.escape(name)}"', m.group(2)):
                text = m.group(3)
                if m.group(1) == "inuse":  # drop the book:/sign:/screen: keys
                    text = re.sub(r"^\s*\w+:\s*", "", text, flags=re.M)
                chars |= set(text)
        for m in re.finditer(r'<typeface>(.*?)</typeface>', body, re.S):
            t = yaml.safe_load(m.group(1)) or {}
            if t.get("font") == name:
                src = t.get("source") or {}
                for v in [t.get("display", ""), t.get("headline", ""), t.get("text", "")] + (t.get("words") or []) + (src.get("lines") or []):
                    chars |= set(str(v))
                chars.add("କ")  # vowel signs show on it in the glyph grid
    return "".join(sorted(chars - set("\n\r\t")))


def metrics(font):
    """Ascender, descender and the height of the consonants, in font units."""
    os2, glyphs, cmap = font["OS/2"], font.getGlyphSet(), font.getBestCmap()
    tops = []
    for c in range(0x0B15, 0x0B3A):
        if c in cmap:
            pen = BoundsPen(glyphs)
            glyphs[cmap[c]].draw(pen)
            if pen.bounds:
                tops.append(pen.bounds[3])
    style = next((r.toUnicode() for r in font["name"].names if r.nameID == 2), "Regular")
    return {"upm": font["head"].unitsPerEm, "ascender": os2.sTypoAscender, "descender": os2.sTypoDescender,
            "letter": round(sorted(tops)[len(tops) // 2]) if tops else os2.sxHeight,
            "weight": os2.usWeightClass, "style": style}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    name, source = sys.argv[1], Path(sys.argv[2]).expanduser()
    text = texts_for(name)
    if not text:
        sys.exit(f"No <specimen>, <inuse> or <typeface> block uses font=\"{name}\".")
    font = TTFont(source)
    out = ROOT / "assets" / "fonts" / f"{name}.woff2"
    out.with_suffix(".json").write_text(json.dumps(metrics(font)) + "\n")
    opts = subset.Options()
    opts.layout_features = ["*"]  # keep conjuncts and vowel-sign shaping
    opts.name_IDs = ["*"]
    opts.flavor = "woff2"
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(out)
    print(f"{out.relative_to(ROOT)}: {len(text)} characters, {len(font.getGlyphOrder())} glyphs, "
          f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
