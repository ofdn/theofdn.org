#!/usr/bin/env python3
"""Make the cut-down copy of an unreleased font for the website.

  python3 scripts/subset_fonts.py chapakala19 /path/to/Chapakala19Regular.woff2

Keeps only the characters that <specimen> and <inuse> blocks use with this
font, plus the conjuncts and shapes those characters need. Writes
assets/fonts/<name>.woff2. Run it again after changing the sample text or
getting a new export. The full font stays outside this repository.

Needs the Python packages fonttools and brotli.
"""
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

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
    return "".join(sorted(chars - set("\n\r\t")))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    name, source = sys.argv[1], Path(sys.argv[2]).expanduser()
    text = texts_for(name)
    if not text:
        sys.exit(f"No <specimen> or <inuse> block uses font=\"{name}\".")
    font = TTFont(source)
    opts = subset.Options()
    opts.layout_features = ["*"]  # keep conjuncts and vowel-sign shaping
    opts.name_IDs = ["*"]
    opts.flavor = "woff2"
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    out = ROOT / "assets" / "fonts" / f"{name}.woff2"
    out.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(out)
    print(f"{out.relative_to(ROOT)}: {len(text)} characters, {len(font.getGlyphOrder())} glyphs, "
          f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
