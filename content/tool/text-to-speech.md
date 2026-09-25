---
title: "Lekatha: Text-to-speech toolkit"
path: "/openspeaks/text-to-speech/"
ark: ofdn-t-000003
tier: "live"
section: "tool"
wp_type: "post"
wp_id: 1761
date: "2019-08-26"
modified: "2021-07-13"
categories:
  - "OpenSpeaks"
  - "Toolkits"
tags:
  - "Archived post"
  - "OER"
  - "OpenSpeaks"
  - "Pronunciation"
  - "resources"
  - "Toolkit"
  - "tutorials"
excerpt: "An experimental text-to-speech (TTS) project that has currently been archived with all source codes and documentation licensed openly."
embeds:
  - provider: "commons"
    id: "File:SOUKO.wav"
  - provider: "commons"
    id: "File:SOAKO.wav"
  - provider: "commons"
    id: "File:SIKI.wav"
  - provider: "commons"
    id: "File:SIKA.wav"
  - provider: "commons"
    id: "File:KOUSI.wav"
  - provider: "commons"
    id: "File:KOASO.wav"
  - provider: "commons"
    id: "File:KESOU.wav"
  - provider: "commons"
    id: "File:KESI.wav"
  - provider: "commons"
    id: "File:KISO.wav"
  - provider: "commons"
    id: "File:KASA.wav"
  - provider: "commons"
    id: "File:KOSI.wav"
  - provider: "commons"
    id: "File:KOSA.wav"
  - provider: "commons"
    id: "File:KOSO.wav"
original_url: "https://theofdn.org/openspeaks/text-to-speech/"
---
![OpenSpeaks logo (black)](/assets/logos/openspeaks.webp)

### This was a part of OpenSpeaks toolkits library and is kept here for archival purposes. See all the [toolkits](/category/openspeaks/toolkit/)…

**Lekatha** is a text-to-speech (TTS) project which is in its infancy at the moment. The word *lekatha* does not mean anything but it is constructed from two [Odia-language](https://en.wikipedia.org/wiki/Odia_language "w:Odia language") words *ଲେଖା* (*lekha*, meaning text) and *କଥା* (*katha*, meaning voice) which refers to constructed voice from text by using a TTS engine.

*Find source code/fork Lekatha on* [![GitHub Logo.png](/assets/logos/github.webp)](https://github.com/OdiaWikimedia/Lekatha)

What does it do?

If Lekatha is a locomotive, its engine is a Python-based [TTS tool](https://github.com/alexram1313/text-to-speech-sample) that was originally written by written by [Alex I. Ramirez](https://github.com/alexram1313). Thanks to Alex who released this as an open source software. The code and the workflow for Odia was then created by Subhashish Panigrahi.

Lekatha’s workflow can be understood in four basic steps:

1.  Each phoneme of an Odia word is converted into Latin-character equivalent using [a converter](https://en.wikipedia.org/wiki/or:%E0%AC%89%E0%AC%87%E0%AC%95%E0%AC%BF%E0%AC%AA%E0%AC%BF%E0%AC%A1%E0%AC%BC%E0%AC%BF%E0%AC%86:%E0%AC%9F%E0%AD%81%E0%AC%B2/%E0%AC%93%E0%AC%A1%E0%AC%BC%E0%AC%BF%E0%AC%86%E2%86%92%E0%AC%B2%E0%AC%BE%E0%AC%9F%E0%AC%BF%E0%AC%A8,_%E0%AC%93_%E0%AC%93%E0%AC%A1%E0%AC%BC%E0%AC%BF%E0%AC%86_%E0%AC%AB%E0%AD%8B%E0%AC%A8%E0%AD%87%E0%AC%9F%E0%AC%BF%E0%AC%95_%E0%AC%9F%E0%AD%8D%E0%AC%B0%E0%AC%BE%E0%AC%A8%E0%AD%8D%E0%AC%B8%E0%AC%95%E0%AD%8D%E0%AC%B0%E0%AC%BF%E0%AC%AA%E0%AC%B8%E0%AC%A8 "w:or:ଉଇକିପିଡ଼ିଆ:ଟୁଲ/ଓଡ଼ିଆ→ଲାଟିନ, ଓ ଓଡ଼ିଆ ଫୋନେଟିକ ଟ୍ରାନ୍ସକ୍ରିପସନ"). For this, an Odia–Latin [transcription chart](https://commons.wikimedia.org/wiki/OpenSpeaks/toolkit/Lekatha#Odia_transcription_chart) (just like [Arpabet](https://en.wikipedia.org/wiki/Arpabet "w:Arpabet")) was created that clearly defines a Latin equivalent of Odia phonemes.
2.  The output from the converter is copied into a text file
3.  Each phoneme is recorded and saved as a `.wav` file in a folder. For instance, the Odia phoneme “କା”‘s Latin equivalent is “KA” and the audio file is named as `KA.wav`.
4.  When the tool is run, it asks for a word or phrase. Here one has to input the word in Latin alphabet. The tool then matches with the recorded phonemes, joins multiple phonemes to create a word

### Odia transcription chart

|              |                  |              |                  |
|--------------|------------------|--------------|------------------|
| Odia phoneme | Latin equivalent | Odia phoneme | Latin equivalent |
| ଅ            | OO               | ଞ            | NY               |
| ଅ            | O                | ଟ            | T                |
| ଆ            | AA               | ଠ            | TH               |
| ା            | A                | ଡ            | D                |
| ଇ            | II               | ଡ଼            | RD               |
| ି             | I                | ଢ            | RH               |
| ଈ            | II               | ଢ଼            | RDH              |
| ୀ            | I                | ଣ            | NN               |
| ଉ            | UU               | ତ            | TT               |
| ୁ             | U                | ଥ            | TTH              |
| ଏ            | EE               | ଦ            | DD               |
| େ            | E                | ଧ            | DDH              |
| ଐ            | OI               | ନ            | N                |
| ୈ            | OY               | ପ            | P                |
| ଓ            | OOA              | ଫ            | PH               |
| ୋ            | OA               | ବ            | B                |
| ଔ            | OOU              | ଭ            | BH               |
| ୌ            | OU               | ମ            | M                |
| ଋ            | RRU              | ଯ            | J                |
| ୃ             | RU               | ର            | R                |
| ୍ୟ            | Y                | ଳ            | LL               |
| କ            | K                | ଲ            | L                |
| ଖ            | KH               | ୱ            | UO               |
| ଗ            | G                | ସ            | S                |
| ଘ            | GH               | ହ            | H                |
| ଙ            | UN               | କ୍ଷ           | KY               |
| ଚ            | C                | ଜ୍ଞ           | GN               |
| ଛ            | CH               | ଂ            | NG               |
| ଜ            | J                | ଁ             | MM               |
| ଝ            | JH               |              |                  |

### Test run

A small set of phonemes were recorded to test how it works. Not all the examples below are real words but they were constructed to see how the tool works with different phoneme combination.How to test the tool for your language?

|           |                  |                          |                   |
|-----------|------------------|--------------------------|-------------------|
| Odia word | Latin equivalent | Odia Transcription Chart | Synthesized audio |
| ସୌକ       | SOUKO            | SOU KO                   | [[embed:0]]   |
| ସୋକ       | SOAKO            | SOA KO                   | [[embed:1]]   |
| ସିକି        | SIKI             | SI KI                    | [[embed:2]]   |
| ସିକା       | SIKA             | SI KA                    | [[embed:3]]   |
| କୌସି       | KOUSI            | KOU SI                   | [[embed:4]]   |
| କୋସ       | KOASO            | KOA SO                   | [[embed:5]]   |
| କେସୌ      | KESOU            | KE SOU                   | [[embed:6]]   |
| କେସି       | KESI             | KE SI                    | [[embed:7]]   |
| କିସ        | KISO             | KI SO                    | [[embed:8]]   |
| କାସା      | KASA             | KA SA                    | [[embed:9]]   |
| କସି        | KOSI             | KO SI                    | [[embed:10]]  |
| କସା       | KOSA             | KO SA                    | [[embed:11]]  |
| କସ        | KOSO             | KO SO                    | [[embed:12]]  |

#### Prerequisites

- A computer running Linux/MacOS (preferably upgraded to latest available stable OS version)
- Python 3 or above (Download the latest stable version from [here](https://www.python.org/downloads/). Please note you might already have Python 2.7 or any other version lower than Python 3. Do ***NOT*** delete them.)
- PyAudio (downloading and installation [here](https://people.csail.mit.edu/hubert/pyaudio/#Installation))
- Audacity (download the latest version from [here](http://www.audacityteam.org/download/))
- Wordlist containing words of your language in the following format in a text file:

`<Word in Latin alphabet><space><space><Phonetic transcription>` It would like below:

    WORD WO AR D

For instance, the Odia language word `କସି` should be added in the text file as:

    KOSI KO SI

The phonetic transcription for each language is different. If your language is written in Latin alphabet then you can use this [**tool**](http://www.speech.cs.cmu.edu/tools/lextool.html) for creating a wordlist that can straightaway be used for our software. If not, then you can first create a phonetic transcription like the one showed [here for\
](https://commons.wikimedia.org/wiki/OpenSpeaks/toolkit/Lekatha#Odia_phonetic_transcription)

[Odia](https://commons.wikimedia.org/wiki/OpenSpeaks/toolkit/Lekatha#Odia_phonetic_transcription).

#### Steps

- Install Python3, Pyaudio and Audacity
- Download the [tool](https://github.com/OdiaWikimedia/Lekatha/archive/master.zip), and unzip it
- Go to the “sounds” folder and delete everything.
- Record all the [phonemes](https://en.wikipedia.org/wiki/phoneme "w:phoneme") of your language using Audacity, and save them exactly the way you have transcribed your phonemes. For instance, if a phoneme is defined as “KO”, you need to save it as `KO.wav`. Ideally all the phonemes of your language should be there in order to make it work for your language but you can record only a few to test it.
- Edit the “wordlist.txt” inside your folder, and replace everything with a list of words (see the [previous section](https://commons.wikimedia.org/wiki/OpenSpeaks/toolkit/Lekatha#Prerequisites) to learn how to create one for your language), and save it
- Run your Linux/Mac Terminal and use the `cd FILELOCATION` to locate the folder

For instance, if your “Lekatha” folder is located in Desktop you need to type:

`cd Desktop`

`cd Lekatha`

- Now type:

`python3 load.py`

You will see a message “`Enter a word or phrase:`“

- Type the word in Latin alphabet e.g. “KOSI” and enter
- It should ideally pronounce the word

### Licensing

- All the software components are licensed under a GNU General Public License v. 3.0 and the text/audio-visual and documentations are licensed under Creative Commons Attribution-ShareAlike 4.0 license
- While forking the software please attribute to the following:

<!-- -->

     Original software: Alex I. Ramirez, Apache License 2.0. <https://github.com/alexram1313/text-to-speech-sample>. Derivative: Subhashish Panigrahi, GNU General Public License v3.0. <https://github.com/OdiaWikimedia/Lekatha>

- While making derivatives of anything other than the software, please attribute to the following:

<!-- -->

    Subhashish Panigrahi, 2017, CC-BY-SA 4.0
