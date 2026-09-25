"""Give a page an ARK id: the next free number for the kind of page.

    python3 scripts/add_ark.py content/archive/dti2018.md resource

Kinds are listed under ark_kinds in data/site.yml. Works on any page, live or
archived, blog posts included. Refuses a page that already has an id.
"""
import re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
KINDS = yaml.safe_load((ROOT / "data" / "site.yml").read_text())["ark_kinds"]


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in KINDS:
        sys.exit(f"usage: add_ark.py <page.md> <{'|'.join(KINDS)}>")
    page, letter = Path(sys.argv[1]), KINDS[sys.argv[2]]
    text = page.read_text()
    head = text.split("\n---", 1)[0]
    if re.search(r"^ark:", head, re.M):
        sys.exit(f"{page} already has an ark; ids never change")
    used = [int(m) for f in (ROOT / "content").rglob("*.md")
            for m in re.findall(rf"^ark: ofdn-{letter}-(\d{{6}})\s*$", f.read_text(), re.M)]
    new = f"ofdn-{letter}-{max(used, default=0) + 1:06d}"
    text, n = re.subn(r"^(path: .*)$", rf"\1\nark: {new}", text, count=1, flags=re.M)
    if not n:
        sys.exit(f"{page} has no path line")
    page.write_text(text)
    print(f"{page}: ark: {new}")


if __name__ == "__main__":
    main()
