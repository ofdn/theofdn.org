# theofdn.org

Source of theofdn.org. Pages are Markdown files in `content/`. GitHub builds and publishes the site on every commit.

## Edit a page

1. Open the file in `content/<section>/`.
2. Change the text. Keep the block between the two `---` lines at the top.
3. Commit. The site rebuilds in about two minutes.

## Sections

| Folder | For | Layout |
|---|---|---|
| `film` | Documentary films | Film page with a details column |
| `podcast` | Podcast episodes | Same as films |
| `oer` | Open educational resources | Module page, with citation |
| `tool` | Language tools and toolkits | Module page, with citation |
| `audio-archive` | Audio archives | Module page, with citation |
| `blog` | New blog posts | Plain page, listed under Publications |
| `archive` | Old posts kept as a record | Plain page with an "Archived" note |
| `hub` | Main pages (home, OpenSpeaks, Initiatives) | Plain page |
| `about` | About, contact, donate, policies | Plain page |

## Fields at the top of a page

- `title`: page title. Any script.
- `path`: the page address. Lowercase a–z, 0–9 and hyphens, starting and ending with `/`. Do not change it once the page is live.
- `section`: one of the folders above.
- `tier`: `live` or `archive`.
- `date`: `2026-09-24`.
- `excerpt`: one or two sentences for lists and search engines.
- `authors`: list of names. Adds the "Cite this page" box on module pages.
- `embeds`: video and audio. `[[embed:0]]` in the text places the first one.
- `transcript`: optional, for films and podcast episodes.
- `ark`: ARK identifier, once the page has one.

## Add a page, blog post or subpage

1. Create a file in the right folder, for example `content/blog/odia-ocr-2026.md`. The file name does not show on the site.
2. Start it with this block:

```
---
title: "ଓଡ଼ିଆ OCR: what we learnt"
path: "/blog/odia-ocr-2026/"
section: "blog"
tier: "live"
date: "2026-09-24"
excerpt: "One or two sentences."
---
```

3. Write the text below the block in Markdown.
4. Commit.

The `path` sets the address, so a title in any script can have a plain Latin address. For a subpage, put it under the parent's address: `/openspeaks/new-toolkit/` sits under `/openspeaks/`.

The build stops with a message if a `path` has other characters or two pages share one.

## Add a video or audio

Add it under `embeds` and put `[[embed:0]]` where it should appear:

```
embeds:
  - provider: "youtube"
    id: "tv65MADEM3M"
```

Providers:

- `youtube`: video ID
- `vimeo`: video number
- `archive`: Internet Archive item name
- `soundcloud`: `tracks/<number>`
- `commons`: `File:Name.wav`
- `file`: link to an audio or video file
- `link`: any other page

## Images and files

1. Put the file in `assets/media/<year>/<month>/`. JPEG, PNG or GIF is fine.
2. Link it in the page as `/assets/media/...`. Add alt text.
3. Run `python3 scripts/optimise_media.py`.

The script makes a WebP copy and a small fallback for old phones, and updates the link. The original moves to `../theofdn-media-originals/`, outside the repository. Keep that folder backed up.

## Spelling

1. Run `python3 scripts/spellcheck.py`.
2. Open `qa/spelling.csv`. In `decision`, write `y` to accept, write your own word, or leave it blank.
3. Run `python3 scripts/spellcheck.py --apply`.

Add words that are correct, such as language terms, to `qa/spelling-ignore.txt`.

## Export from WordPress

`scripts/export_theofdn.py` copied the WordPress site on 24 September 2026. It stops if `content/` exists. Do not run it with `--force` after editing, as that overwrites your edits.

## Build and preview

1. Run `python3 scripts/build.py`. The site goes to `_site/`.
2. Run `python3 -m http.server -d _site 8000`.
3. Open `http://localhost:8000`.

Needs pandoc and the Python packages `pyyaml`, `jinja2` and `beautifulsoup4`.

## Publishing

GitHub builds the site on every commit to `main` (`.github/workflows/publish.yml`).

- Test address: `ofdn.github.io/theofdn.org`. The repository variable `BASE_PATH` is `/theofdn.org`.
- To move to theofdn.org:
  1. Set `BASE_PATH` to empty.
  2. Add the domain under Settings, Pages.
  3. Point the DNS to GitHub.
