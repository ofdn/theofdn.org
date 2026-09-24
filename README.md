# theofdn.org

Source of theofdn.org. Pages are Markdown files in `content/`. GitHub builds and publishes the site on every commit.

## Edit a page

1. Open the file in `content/<section>/`.
2. Change the text. Keep the block between the two `---` lines at the top.
3. Commit. The site rebuilds in about two minutes.

## Site status

Open `data/site.yml` and set `status`:

- `live`: the normal site. This is the default.
- `maintenance`: every page shows a short "being updated" notice instead of its content. Search engines are asked not to index it.
- `archive`: every page shows a yellow notice at the top saying the site is archived. The content stays.

Commit. The change is live in about two minutes. Set it back to `live` when the work is done.

For one page only, add `status: archive` or `status: maintenance` at the top of that page. `status_message` replaces the standard wording for that page. `archive_message` and `maintenance_message` in `data/site.yml` do the same for the whole site.

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
- `lede`: optional short line under the title on film and podcast pages.
- `authors`: list of names. Adds the "Cite this page" box on module pages.
- `embeds`: video and audio. `[[embed:0]]` in the text places the first one.
- `transcript`: optional, for films and podcast episodes.
- `ark`: ARK identifier, once the page has one.
- `status`: optional. `archive` or `maintenance` for this page only. See "Site status".

## Film page fields

All optional. Paths point to files in `assets/images/`.

- `hero`: large image at the top, without text.
- `hero_portrait`: version of the hero for phones.
- `title_image`: the film title as an image, shown over the hero.
- `laurels`: award and selection laurels, shown over the hero. Each has `src` and `alt`.
- `poster`: theatrical poster, shown in the details column.
- `trailer`: video after the hero. Same form as an entry in `embeds`.
- `details`: datasheet rows. Each has `label` and a `value` list.
- `press_kit`: link to the press kit.
- `stills`: list of still images, shown at the end. A click opens the still in a large view on the same page.
- `listen`: podcast links. Each has `label` and `url`.
- `links`: IMDb, DOI, Moviebuff, Letterboxd, Wikidata, Library of Congress and similar pages. One address per line. They show in the details column with a small icon. Do not add logo images in the text.

```
links:
- https://www.imdb.com/title/tt12663954/
- https://doi.org/10.17613/frzt-b139
```

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

## Quotes

Write every quote the same way. The site gives them all one look.

```
> “Loving homage to family and culture.”
>
> — **Rebecca Cherry**, *Film Carnage*
```

The last line starts with a dash. Put the name in bold and the source in italics. Quotes one after another show as a grid.

For a star rating, start the quote with a line such as `★★★★☆ (4 out of 5)`. The page shows the stars. Screen readers read "Rated 4 out of 5".

## Section links

Every heading gets a link that copies its address. No extra step needed.

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
