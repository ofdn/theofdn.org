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

Every page uses one template. A part of the page shows only when its field is filled in. Any page can have an infobox, a byline or posters.

Always needed:

- `title`: page title. Any script.
- `path`: the page address. Lowercase a–z, 0–9 and hyphens, starting and ending with `/`. Follow the pattern under Addresses. Do not change it once the page is live; if you must, see Move a page.
- `section`: one of the folders above.
- `tier`: `live` or `archive`.
- `date`: `2026-09-24`.
- `excerpt`: one or two sentences for lists and search engines.

Optional, on any page:

- `lede`: short line under the title.
- `authors`: list of names. Adds the names and date under the title, and "Cite this page" at the end.
- `ark`: ARK id, such as `ofdn-f-000001`. Shows a permanent link under the title. See "ARK identifiers".
- `embeds`: video and audio. `[[embed:0]]` in the text places the first one.
- `transcript`: shown after the text.
- `status`: `archive` or `maintenance` for this page only. See "Site status".

Infobox (a column beside the text). Film and podcast pages always have one; other pages get one when any of these is set:

- `info`: the rows, as `field: value`. Every field is listed once in `data/fields.yml`, with its label and order. A field means the same on every page. Any page can use any field: a font can have `doi`, a film can have `licence`. For several values, use a list. To add a new field, add it to `data/fields.yml` first. The build stops on a field that is not there.
- `info_title`: heading of the infobox. Default: "Film details", "Episode details" or "Details".
- `links`: IMDb, DOI, Moviebuff, Letterboxd, Wikidata, Library of Congress and similar pages. One address per line. They show with a small icon. Do not add logo images in the text.
- `listen`: podcast links. Each has `label` and `url`.
- `press_kit`: link to the press kit.

```
info:
  director: Subhashish Panigrahi
  producer: Subhashish Panigrahi
  language: Remosam (Bonda), Odia
  doi: 10.5240/B222-043E-AFAA-EC7B-F5F6-2
links:
- https://www.imdb.com/title/tt12663954/
```

Roles held by the same person join into one row ("Director and producer"). A bare DOI or LCCN number becomes a link.

For an infobox inside the text, use an `<info>` block. One per typeface on a page is an example. `image` and `alt` put a picture beside the rows:

```
<info>
image: /assets/images/type-chapakala19-poster.svg
alt: Chapakala 19 typeface poster
script: Odia
designer: Subhashish Panigrahi
licence: SIL Open Font License 1.1
</info>
```

To split a page into sections, put `---` on its own line, with an empty line above it. A section with an `<info>` block gets the film layout: its heading on top, the infobox beside the rest. Other sections look as usual.

A type tester shows sample text in a font. Readers can type their own text and change the size:

```
<specimen font="chapakala19" name="Chapakala 19">ଉକ୍ତ ଅଛି, “କେହି ଯେବେ ଆପଣା ସ୍ତ୍ରୀକୁ</specimen>
```

`font` is a file in `assets/fonts/`, without `.woff2`.

Before a font is released, keep the full file out of this repository. List the font under `preview_fonts` in `data/site.yml`, then run:

```
python3 scripts/subset_fonts.py chapakala19 ~/path/to/Chapakala19Regular.woff2
```

This writes a small copy with only the characters used on the site. Readers can change the size but cannot type their own text. Run it again after a new export or a change to the sample text. On release, remove the font from `preview_fonts` and copy the full `.woff2` into `assets/fonts/`.

To show a subtitle under a section heading, put one line in italics right below it:

```
## Chapakala 19
*Revival of 19th-century Odia typeface*
```

To show the font in use, list up to three settings. Each shows the text in a simple frame:

```
<inuse font="chapakala19" name="Chapakala 19">
book: ଉକ୍ତ ଅଛି, “କେହି ଯେବେ ଆପଣା ସ୍ତ୍ରୀକୁ
sign: କଟକ
screen: ନମସ୍କାର
</inuse>
```

Images and video. Paths point to files in `assets/images/`:

- `hero`: large image at the top, without text.
- `hero_portrait`: version of the hero for phones.
- `title_image`: the title as an image, shown over the hero.
- `laurels`: award and selection laurels, shown over the hero. Each has `src` and `alt`.
- `trailer`: video under the title. Same form as an entry in `embeds`.
- `poster`, `posters`: shown in a Posters section at the end. `poster_credit` is the caption.
- `stills`: list of still images, shown at the end. A click opens the still in a large view on the same page.

## ARK identifiers

O Foundation's ARK NAAN is 15056. Any page can have an ARK: live or archived, a blog post too. Give one to pages people will cite or link to for a long time.

Ids take the form `ofdn-<letter>-<six digits>`. The letter is the kind of page:

- `f` film or video
- `a` audio: podcast episodes and audio archives
- `r` resource: an OER, guide, tutorial, toolkit, handbook, report or white paper
- `t` tool
- `y` typeface
- `d` dataset

To ask for an ARK, write the kind at the top of the page and commit:

```yaml
ark: resource
```

GitHub gives the page the next free id and commits it back, for example `ark: ofdn-r-000008`. Pull before your next edit. If a page cannot get an id, the Actions run shows a warning. That page waits, and the rest of the site still publishes.

To do the same on your computer: `python3 scripts/add_ark.py --pending`.

The kinds are listed under `ark_kinds` in `data/site.yml`. To add a kind, add a line there with an unused letter. Never change or remove a letter once an id with it is published.

Never change or reuse an id once it is published. Do not delete a page that has an ARK; set `status: archive` on it instead. If a page moves, change its `path` and add a redirect (see Move a page); the ARK follows it. A language version gets `/<lang>` after the ARK on its own.

### Files: PDF, video, audio, subtitles

The ARK itself always points to the page. A file that belongs to the page gets the same ARK with a word after it, as UNESCO does:

- `ark:15056/ofdn-r-000008` is the page.
- `ark:15056/ofdn-r-000008/pdf` is the PDF.

This holds whether the page embeds the PDF or only links to it. Add the files under `ark_parts`. Leave `pdf:` empty to use the one PDF in `/assets/docs/` that the page links to; GitHub fills in the path.

```yaml
ark: resource
ark_parts:
  pdf:
  video: https://archive.org/details/example
  subtitles/en: /assets/docs/example-en.srt
```

The words are `video`, `audio`, `pdf`, `transcript`, `subtitles` and `files`. Add a second word for a version, such as `subtitles/en` or `pdf/or`. Each one is shown under the page's permanent link. Give ARKs only to files O Foundation made, not to PDFs by others that a page links to.

### How the links work

`https://n2t.net/ark:15056/<id>` sends readers to `theofdn.org/ark:15056/<id>`, which the build points to the page. This works only once theofdn.org serves this site.

## Addresses

| Page | Address |
|---|---|
| Resource: OER, tool, toolkit, handbook, audio archive | `/resources/<slug>/` |
| Language version of a resource | `/resources/<slug>/<lang>/` |
| The running tool itself | `/tools/<slug>/` |
| Blog post, announcement, meeting notes | `/blogs/<slug>/` |
| Language version of a blog post | `/blogs/<slug>/<lang>/` |
| Film, podcast episode | `/film/<slug>/`, `/podcast/<slug>/` |
| ARK of a page | `ark:15056/<id>` |
| ARK of a language version | `ark:15056/<id>/<lang>` |

- One resource has one page. It carries the ARK.
- An announcement is a blog post. It links to the resource page. It does not repeat the tool.
- A blog post has no category in its address: `/blogs/wikimania2019/`, not `/blogs/conference/wikimania2019/`.
- `<slug>` is short, lowercase and in Latin letters. Use the name people know the resource by.

Example:

- Resource: `/resources/santali-unicode-converter/`
- Santali version: `/resources/santali-unicode-converter/sat/`
- The converter: `/tools/santali-unicode-converter/`
- Announcement: `/blogs/santali-unicode-converter-release/`
- ARK: `ark:15056/ofdn-t-000001`, and `ark:15056/ofdn-t-000001/sat` for the Santali version

## Move a page

1. Change `path` at the top of the page.
2. Add a line to `data/redirects.json`: `"/old/address/": "/new/address/"`. The old address then forwards to the new one.
3. If other redirects point to the old address, point them to the new one.
4. Search `content/` for links to the old address and change them. Leave `original_url` as it is.

The ARK follows the page. Never remove a line from `data/redirects.json`.

## Language versions

A language version is the same page in another language. It is not a new page.

1. Copy the page file and add the language code before `.md`: `santali-unicode-converter.md` becomes `santali-unicode-converter.sat.md`. Use the ISO 639 code.
2. Keep the file in the same folder.
3. At the top, set `lang` to the code and `path` to the original address plus the code:

```
---
title: "ᱥᱟᱱᱛᱟᱲᱤ ᱤᱭᱩᱱᱤᱠᱚᱰ ᱠᱚᱱᱵᱷᱚᱴᱚᱨ ᱥᱚᱫᱚᱨᱮᱱᱟ"
path: "/resources/santali-unicode-converter/sat/"
lang: sat
section: "tool"
translators:
  - Full Name
tier: "live"
date: "2019-07-14"
excerpt: "One or two sentences in the language."
---
```

4. Translate the title, excerpt and text.
5. New language? Add it under `languages` in `data/site.yml`, with its own name and its English name.
6. Commit.

The original keeps the short address, in whatever language it was first written. A page first written in Santali has its English version at `/<slug>/en/`.

Each version shows "Also in" links to the others, and lists show one card per page with its languages. A version shares the ARK of the original, with the code after it. Do not give a version its own `ark`.

Name every translator in `translators`. The names show on the page.

## Add a page, blog post or subpage

1. Create a file in the right folder, for example `content/blog/odia-ocr-2026.md`. The file name does not show on the site.
2. Start it with this block:

```
---
title: "ଓଡ଼ିଆ OCR: what we learnt"
path: "/blogs/odia-ocr-2026/"
section: "blog"
tier: "live"
date: "2026-09-24"
excerpt: "One or two sentences."
---
```

3. Write the text below the block in Markdown.
4. Commit.

The `path` sets the address, so a title in any script can have a plain Latin address. Use the patterns under Addresses.

The build stops with a message if a `path` has other characters or two pages share one.

## Quotes

Write every quote the same way. The site gives them all one look.

```
> “Loving homage to family and culture.”
>
> — **Rebecca Cherry**, *Film Carnage*
```

The last line starts with a dash. Put the name in bold and the source in italics. Quotes one after another show as a grid.

The short form gives the same result:

```
<quote author="Benjamin Franz" source="Film Threat">Quite a visual treat.</quote>
```

`author` and `source` are both optional. Leave both out for a quote with no name under it.

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

To add a caption, put it on the line after the image:

```
![Two elders singing wedding songs](/assets/images/remosam-poster.webp)
<c>Poster of “Remosam”. © Subhashish Panigrahi, CC BY-SA 4.0</c>
```

Links and italics work inside a caption. A caption without an image above it shows as a small caption line.

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

## Licences

- Original content: CC BY-SA 4.0, unless a page says otherwise.
- Copyright material used under fair use: say so clearly on that page.
- Site code: Anti-Capitalist Software License (v 1.4), in `LICENSE`.
- `tools/santali-unicode-converter/`: MIT, by Jnanaranjan Sahu.
- Fonts: their own licence, shown on the font's page.

## Publishing

GitHub builds the site on every commit to `main` (`.github/workflows/publish.yml`).

- Test address: `new.theofdn.org` (Cloudflare DNS, custom domain under Settings, Pages). `ofdn.github.io/theofdn.org` redirects there.
- To serve the site under a path instead, such as `/theofdn.org`, set the repository variable `BASE_PATH` to that path. Leave it unset for a domain. GitHub does not accept an empty variable; delete it instead.
- To move to theofdn.org:
  1. Change the custom domain under Settings, Pages to `theofdn.org`.
  2. In Cloudflare, point `theofdn.org` to GitHub.
  3. Check the ARK links (see "ARK identifiers").
