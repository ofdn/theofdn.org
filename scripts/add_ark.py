"""Mint ARK ids: the next free number for the kind of page.

To ask for an ARK, write the kind instead of an id at the top of the page:

    ark: resource
    ark_parts:
      pdf:

On every push, GitHub runs `add_ark.py --pending`, which swaps each kind for
the next free id (ark: ofdn-r-000009) and fills an empty `pdf:` with the one
PDF from /assets/docs/ that the page links to. It then commits the change.

The same can be done by hand for one page:

    python3 scripts/add_ark.py content/archive/dti2018.md resource

Kinds are listed under ark_kinds in data/site.yml. Works on any page, live or
archived, blog posts included. An id, once written, never changes.
"""
import re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
KINDS = yaml.safe_load((ROOT / "data" / "site.yml").read_text())["ark_kinds"]
LOCAL_PDF = re.compile(r"(/assets/docs/[^\s)\"'<>]+\.pdf)")


def split(text):
    """Front matter and body."""
    if not text.startswith("---\n"):
        return None, text
    head, _, body = text[4:].partition("\n---")
    return head, body


def next_id(letter):
    used = [int(m) for f in (ROOT / "content").rglob("*.md")
            for m in re.findall(rf"^ark: ofdn-{letter}-(\d{{6}})\s*$", f.read_text(), re.M)]
    return f"ofdn-{letter}-{max(used, default=0) + 1:06d}"


def fill_parts(page, head, body):
    """An empty `pdf:` under ark_parts becomes the page's own PDF."""
    parts = (yaml.safe_load(head) or {}).get("ark_parts") or {}
    for q, target in parts.items():
        if target:
            continue
        if not str(q).startswith("pdf"):
            sys.exit(f"{page}: ark_parts: {q} needs a link or file path")
        pdfs = sorted(set(LOCAL_PDF.findall(body)))
        if len(pdfs) != 1:
            sys.exit(f"{page}: ark_parts: {q} is empty and the page links to {len(pdfs)} PDFs "
                     f"in /assets/docs/; write the path after {q}:")
        head = re.sub(rf"^(\s+{re.escape(str(q))}):[ \t]*$", rf"\1: {pdfs[0]}", head, count=1, flags=re.M)
    return head


def mint(page, kind=None):
    """Give one page its id. Returns the new id, or None if nothing to do."""
    text = page.read_text()
    head, body = split(text)
    if head is None:
        return None
    m = re.search(r"^ark:[ \t]*(\S*)[ \t]*$", head, re.M)
    if kind is None:  # --pending: only pages that name a kind
        if not m or m.group(1) not in KINDS:
            return None
        kind = m.group(1)
    elif m and m.group(1) not in KINDS:
        sys.exit(f"{page} already has an ark; ids never change")
    new = next_id(KINDS[kind])
    if m:
        head = head[:m.start()] + f"ark: {new}" + head[m.end():]
    else:
        head, n = re.subn(r"^(path: .*)$", rf"\1\nark: {new}", head, count=1, flags=re.M)
        if not n:
            sys.exit(f"{page} has no path line")
    head = fill_parts(page, head, body)
    page.write_text("---\n" + head + "\n---" + body)
    return new


def main():
    if sys.argv[1:] == ["--pending"]:
        # A page that cannot be minted is skipped with a warning (shown on the
        # GitHub Actions run) and waits; the rest of the site still publishes.
        for page in sorted((ROOT / "content").rglob("*.md")):
            try:
                new = mint(page)
            except SystemExit as e:
                print(f"::warning file={page.relative_to(ROOT)}::{e}")
                continue
            if new:
                print(f"{page.relative_to(ROOT)}: ark: {new}")
        return
    if len(sys.argv) != 3 or sys.argv[2] not in KINDS:
        sys.exit(f"usage: add_ark.py --pending, or add_ark.py <page.md> <{'|'.join(KINDS)}>")
    page = Path(sys.argv[1])
    print(f"{page}: ark: {mint(page, sys.argv[2])}")


if __name__ == "__main__":
    main()
