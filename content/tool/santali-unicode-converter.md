---
title: "Santali (Ol Chiki) Unicode converter"
path: "/tools/sat/unicode-converter/"
ark: ofdn-t-000001
tier: "live"
section: "tool"
wp_type: "post"
wp_id: 528
date: "2018-09-12"
modified: "2019-08-28"
categories:
  - "Language Resources"
  - "Santali"
tags:
  - "santali"
  - "tools"
excerpt: "Converts Santali text typed in older Ol Chiki fonts into Unicode, so that it shows correctly on any phone or computer."
embeds:
  - provider: "converter"
    id: "suc"
    title: "Santali (Ol Chiki) Unicode converter"
original_url: "https://theofdn.org/openspeaks/language-resources/santali-unicode-encoding-converter/"
scope: "For anyone with Santali text typed in an older Ol Chiki font, which shows as Latin letters on other phones and computers."
info_title: About the converter
info:
  developer: "[Jnanaranjan Sahu](https://jsahu.me)"
  release: 12 September 2018
  funder: Shuttleworth Foundation flash grant, from Anasuya Sengupta
  language: "[Santali](/resources/sat/)"
  script: "[Ol Chiki](https://rtd.theofdn.org/scripts/ol-chiki/) (ᱚᱞ ᱪᱤᱠᱤ)"
  repository: "[ofdn/santali-unicode-converter on GitHub](https://github.com/ofdn/santali-unicode-converter)"
  licence: MIT
resources:
  credits:
    - name: Jnanaranjan Sahu
      url: https://jsahu.me
      note: Built the converter and runs the server that converts the text.
    - name: Ramjit Tudu
      url: https://sat.wikipedia.org/wiki/%E1%B1%B5%E1%B1%AE%E1%B1%B5%E1%B1%B7%E1%B1%9F%E1%B1%A8%E1%B1%A4%E1%B1%AD%E1%B1%9F%E1%B1%B9:Ramjit_Tudu
      note: Helped with the character mapping.
---
Much Santali text was typed in older Ol Chiki fonts. These fonts store each Ol Chiki letter as a Latin letter: type "a" and the font draws ᱟ. On a phone or computer without the same font, the text shows only as Latin letters. This converter changes it into Unicode. Then it shows in Ol Chiki on any device, and search engines can find it.

[[embed:0]]

## How to use it

1. Copy the Santali text from your file. Here is an [example of a book typed in an older font](https://web.archive.org/web/20210312035032/https://ova.gov.in/wp-content/plugins/anubada/uploads/09-04-2019-10-27-50-Santali%20(Tri-lingual%20Book).pdf).
2. Paste it in the first box. The Unicode text shows in the second box.
3. Read through the Unicode text and correct any small errors.
4. Select "Copy the Unicode text" and paste it where you need it.

To read the Unicode text, you need an Ol Chiki Unicode font such as [Noto Sans Ol Chiki](https://fonts.google.com/noto/specimen/Noto+Sans+Ol+Chiki). Most Android phones and Windows computers already have one.

## Why it is needed

Michael Everson [proposed](https://www.unicode.org/L2/L1999/n1956.pdf) adding Ol Chiki to Unicode on 29 January 1999. Unicode 5.1 added it in 2008. Until then, Santali fonts each used their own encoding, mostly built on [ASCII](https://en.wikipedia.org/wiki/ASCII). Some publications still use these fonts, such as the Santali magazine Fagun. Their text cannot be searched online. It also cannot be read on a device without the same font.

Read the [blog post on the converter's release](/blogs/santali-unicode-converter-release/) ([ᱥᱟᱱᱛᱟᱲᱤ](/tools/sat/unicode-converter/sat/)) for more.
