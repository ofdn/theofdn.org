#!/usr/bin/env python3
"""British English and typo check for content/*.md.

Writes qa/spelling.csv for review. Nothing in content/ is changed.
Words listed in qa/spelling-ignore.txt (one per line) are skipped.

To apply fixes: fill the "decision" column in qa/spelling.csv, then run
  spellcheck.py --apply
  y        use the first suggestion (for US forms, the British form)
  <text>   use this text instead
  blank    leave as it is
Replacements are whole-word and skip front matter, links and code. Check
quotes from other people and titles of works by hand before saying y.

Kinds in the report:
  us-spelling  US form where British is expected (organize, color, labor)
  typo         word not in the en_GB dictionary, with suggestions
  grammar      grammar note from the macOS checker ("sentence fragment"
               notes are dropped, since headings and table cells trigger them)

Capitalised words, words in other scripts, and words with digits are
skipped, since most are names, places and language terms.
"""
import csv, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "qa"
IGNORE_FILE = QA / "spelling-ignore.txt"

# US forms the en_GB dictionary still accepts, so the checker alone misses them.
US_FORMS = re.compile(
    r"\b(labor(?:s|ed|ing)?|honor(?:s|ed|ing|able)?|color(?:s|ed|ful)?|"
    r"favor(?:s|ed|ite|able)?|behavior(?:s|al)?|neighbor(?:s|hood)?|"
    r"center(?:s|ed|ing)?|catalog(?:s|ed)?|program(?:s)?(?= of| for| in)|"
    r"licenses?(?= (?:is|are|for|of|and|to|was)\b)|"
    r"\w+iz(?:e|es|ed|ing|ation|ations))\b"
)
# Words ending in -ize that are the same in British English.
IZE_OK = {"size", "sizes", "sized", "prize", "prizes", "seize", "seized", "capsize"}


def plain_text(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    md = re.sub(r"`[^`]*`", " ", md)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)
    md = re.sub(r"\]\([^)]*\)", "]", md)
    md = re.sub(r"<[^>]+>", " ", md)
    md = re.sub(r"https?://\S+|www\.\S+|\S+@\S+", " ", md)
    md = re.sub(r"\[\[embed:\d+\]\]", " ", md)
    md = re.sub(r"[*_]", "", md)
    return re.sub(r"[#>|\[\]\\]", " ", md)


def title_of(md):
    m = re.search(r'^title: "(.*)"$', md, flags=re.M)
    return m.group(1) if m else ""


def us_form(word, suggestion):
    """True when the suggestion is the British form of the same word."""
    def norm(w):
        w = w.lower()
        for a, b in (("our", "or"), ("tre", "ter"), ("ae", "e"), ("efact", "ifact"),
                     ("ll", "l"), ("ence", "ense"), ("s", "z")):
            w = w.replace(a, b)
        return w
    # Length guard stops "wil" -> "will" passing as a US form.
    return (word.lower() != suggestion.lower() and norm(word) == norm(suggestion)
            and abs(len(word) - len(suggestion)) <= 2 and len(word) > 4)


def skip(word, ignore):
    return (not word.isascii() or any(c.isdigit() for c in word) or re.search(r"[.:/@]", word)
            or word[:1].isupper() or word.lower() in ignore or len(word) < 3)


def british(word):
    w = re.sub(r"iz(e|es|ed|ing|ation|ations)$", r"is\1", word)
    for a, b in (("labor", "labour"), ("honor", "honour"), ("color", "colour"), ("favor", "favour"),
                 ("behavior", "behaviour"), ("neighbor", "neighbour"), ("center", "centre"),
                 ("catalog", "catalogue"), ("license", "licence"), ("theater", "theatre"),
                 ("artifact", "artefact"), ("enrollment", "enrolment"), ("analyz", "analys")):
        if w.lower().startswith(a):
            w = b + w[len(a):]
    return w


def apply_fixes():
    rows = list(csv.DictReader(open(QA / "spelling.csv")))
    changed = 0
    for r in rows:
        d = r["decision"].strip()
        if not d:
            continue
        new = d if d.lower() != "y" else (british(r["word"]) if r["kind"] == "us-spelling"
                                         else r["suggestions"].split("; ")[0])
        if not new or new == r["word"]:
            continue
        f = ROOT / r["file"]
        md = f.read_text()
        head, sep, body = md.partition("\n---\n")
        # Leave link targets, code and image paths alone.
        parts = re.split(r"(\]\([^)]*\)|`[^`]*`|https?://\S+)", body)
        pat = re.compile(rf"(?<![\w/.-]){re.escape(r['word'])}(?![\w/-])")
        n = 0
        for i in range(0, len(parts), 2):
            parts[i], k = pat.subn(new, parts[i])
            n += k
        if n:
            f.write_text(head + sep + "".join(parts))
            changed += n
    print(f"{changed} replacement(s) written", file=sys.stderr)


def main():
    if "--apply" in sys.argv:
        return apply_fixes()
    ignore = set()
    if IGNORE_FILE.exists():
        ignore = {w.strip().lower() for w in IGNORE_FILE.read_text().splitlines() if w.strip()}
    files = sorted((ROOT / "content").rglob("*.md"))
    docs = []
    for f in files:
        md = f.read_text()
        docs.append({"file": str(f.relative_to(ROOT)), "text": title_of(md) + ".\n" + plain_text(md)})

    r = subprocess.run(["swift", str(ROOT / "scripts" / "spellcheck.swift")],
                       input=json.dumps(docs), capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr)
    findings = json.loads(r.stdout)

    rows = []
    for fd in findings:
        word = fd["text"]
        if fd["kind"] == "spelling":
            if skip(word, ignore):
                continue
            sugg = fd["suggestions"]
            is_us = any(us_form(word, g) for g in sugg)
            rows.append((fd["file"], "us-spelling" if is_us else "typo", word, "; ".join(sugg), fd["context"].strip()))
        elif fd["kind"] == "grammar" and "fragment" not in fd["context"]:
            rows.append((fd["file"], "grammar", word, "; ".join(fd["suggestions"]), fd["context"].strip()))

    seen = {(r[0], r[2].lower()) for r in rows}
    for d in docs:
        for m in US_FORMS.finditer(d["text"]):
            w = m.group(1)
            if w.lower() in IZE_OK or w[:1].isupper() or w.lower() in ignore or (d["file"], w.lower()) in seen:
                continue
            seen.add((d["file"], w.lower()))
            s = d["text"]
            ctx = s[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            rows.append((d["file"], "us-spelling", w, "", ctx.strip()))

    order = {"us-spelling": 0, "typo": 1, "grammar": 2}
    rows.sort(key=lambda r: (order[r[1]], r[0], r[2].lower()))
    QA.mkdir(exist_ok=True)
    with open(QA / "spelling.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "kind", "word", "suggestions", "context", "decision"])
        w.writerows(r + ("",) for r in rows)
    from collections import Counter
    print(dict(Counter(r[1] for r in rows)), f"across {len({r[0] for r in rows})} files", file=sys.stderr)


if __name__ == "__main__":
    main()
