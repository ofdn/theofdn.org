#!/usr/bin/env python3
"""Make images and PDFs light enough for the site.

Folders:
  assets/images/   photos, posters, screenshots: <page>-<what-it-shows>
  assets/logos/    logos, badges, icons: <organisation>
  assets/docs/     PDFs and other documents

For each JPEG, PNG, GIF or WebP in assets/images or assets/logos:
  <name>.webp            main image, at most 1600 px, quality 80
                         (animated GIFs stay animated)
  <name>.fallback.jpg    480 px, quality 60, for browsers without WebP
  <name>.fallback.png    used instead of JPEG when the image is transparent
PDFs are compressed with Ghostscript when that makes them smaller.
File names become lowercase with hyphens.
Links in content/ are updated to the new names.

Originals move to ../theofdn-media-originals/, outside the repository.
Files no page links to also move there.

Run it again after adding new images: it only touches files that are
not converted yet.
"""
import re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FOLDERS = [ASSETS / "images", ASSETS / "logos", ASSETS / "docs"]
CONTENT = ROOT / "content"
ORIG = ROOT.parent / "theofdn-media-originals"
IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAIN_MAX, FALLBACK_MAX = 1600, 480


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def clean_name(name):
    stem, ext = name.rsplit(".", 1) if "." in name else (name, "")
    stem = re.sub(r"[^a-z0-9]+", "-", unquote(stem).lower()).strip("-") or "file"
    return f"{stem}.{ext.lower()}" if ext else stem


def site(path):
    return "/" + path.relative_to(ROOT).as_posix()


def load_pages():
    return {p: p.read_text() for p in CONTENT.rglob("*.md")}


def forms(url):
    """Ways a path can appear in Markdown: raw, or percent-encoded."""
    return {url, quote(url, safe="/"), quote(url, safe="/()")}


def is_referenced(url, pages):
    return any(f in text for text in pages.values() for f in forms(url))


def replace_everywhere(old, new, pages):
    for p, text in pages.items():
        t = text
        for f in sorted(forms(old), key=len, reverse=True):
            t = t.replace(f, new)
        if t != text:
            pages[p] = t


def frames(path):
    r = run("magick", "identify", "-format", "%n\n", str(path))
    try:
        return int(r.stdout.split()[0])
    except (IndexError, ValueError):
        return 1


def has_transparency(path):
    r = run("magick", f"{path}[0]", "-format", "%[opaque]", "info:")
    return r.stdout.strip().lower() == "false"


def convert_image(src, dest_dir, stem):
    main = dest_dir / f"{stem}.webp"
    animated = src.suffix.lower() in (".gif", ".webp") and frames(src) > 1
    if animated:
        r = run("magick", str(src), "-coalesce", "-resize", f"{MAIN_MAX}x{MAIN_MAX}>",
                "-quality", "80", "-loop", "0", str(main))
    else:
        r = run("magick", f"{src}[0]", "-auto-orient", "-resize", f"{MAIN_MAX}x{MAIN_MAX}>",
                "-strip", "-quality", "80", str(main))
    if r.returncode:
        raise RuntimeError(r.stderr)
    if has_transparency(src):
        fb = dest_dir / f"{stem}.fallback.png"
        r = run("magick", f"{src}[0]", "-resize", f"{FALLBACK_MAX}x{FALLBACK_MAX}>", "-strip",
                "-colors", "256", f"PNG8:{fb}")
    else:
        fb = dest_dir / f"{stem}.fallback.jpg"
        r = run("magick", f"{src}[0]", "-auto-orient", "-resize", f"{FALLBACK_MAX}x{FALLBACK_MAX}>",
                "-strip", "-background", "white", "-flatten", "-quality", "60",
                "-sampling-factor", "4:2:0", "-interlace", "JPEG", str(fb))
    if r.returncode:
        raise RuntimeError(r.stderr)
    return main


def compress_pdf(src, dest):
    tmp = dest.with_suffix(".tmp.pdf")
    r = run("gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={tmp}", str(src))
    if r.returncode == 0 and tmp.exists() and tmp.stat().st_size < src.stat().st_size * 0.9:
        tmp.replace(dest)
    else:
        tmp.unlink(missing_ok=True)
        shutil.copy2(src, dest)


def main():
    pages = load_pages()
    files = [f for d in FOLDERS if d.exists() for f in sorted(d.iterdir())]
    before = sum(f.stat().st_size for f in files if f.is_file())
    moved = converted = pdfs = 0

    for f in files:
        if not f.is_file():
            continue
        if f.name == ".DS_Store":
            f.unlink()
            continue
        if ".fallback." in f.name:
            continue
        rel = f.relative_to(ASSETS)
        url = site(f)
        ext = f.suffix.lower()
        done = ext == ".webp" and any(f.with_name(f.stem + s).exists()
                                      for s in (".fallback.jpg", ".fallback.png"))
        # A PDF is done once the site copy has a clean name and sits in docs/
        # (the original then lives in the originals folder).
        done = done or (ext == ".pdf" and f.parent.name == "docs" and f.name == clean_name(f.name))
        if done:
            continue

        archive = ORIG / rel
        if not is_referenced(url, pages) or ext in IMAGE or ext == ".pdf":
            archive.parent.mkdir(parents=True, exist_ok=True)
        if not is_referenced(url, pages):
            shutil.move(str(f), archive)
            moved += 1
            continue

        stem = clean_name(f.name).rsplit(".", 1)[0]
        if ext in IMAGE and (f.parent / f"{stem}.webp").exists() and ext != ".webp":
            stem += "-" + ext[1:]  # e.g. Sunset.jpg and Sunset.png in one folder
        if ext in IMAGE:
            shutil.move(str(f), archive)
            try:
                new = convert_image(archive, f.parent, stem)
            except RuntimeError as e:
                shutil.move(str(archive), f)  # put it back, report, carry on
                print(f"failed: {rel}: {e.strip()[:120]}", file=sys.stderr)
                continue
            replace_everywhere(url, site(new), pages)
            converted += 1
        elif ext == ".pdf":
            shutil.move(str(f), archive)
            new = f.with_name(clean_name(f.name))
            compress_pdf(archive, new)
            replace_everywhere(url, site(new), pages)
            pdfs += 1
        else:
            new = f.with_name(clean_name(f.name))
            if new != f:
                f.rename(new)
                replace_everywhere(url, site(new), pages)

    for p, text in pages.items():
        if p.read_text() != text:
            p.write_text(text)
    after = sum(f.stat().st_size for d in FOLDERS if d.exists() for f in d.iterdir() if f.is_file())
    print(f"images converted: {converted}, PDFs: {pdfs}, unused files moved out: {moved}", file=sys.stderr)
    print(f"assets: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB", file=sys.stderr)


if __name__ == "__main__":
    main()
