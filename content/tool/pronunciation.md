---
title: "Kathabhidhana: Pronunciation Toolkit"
path: "/openspeaks/pronunciation/"
tier: "live"
section: "tool"
wp_type: "post"
wp_id: 1733
date: "2019-08-26"
modified: "2019-08-26"
categories:
  - "OpenSpeaks"
  - "Toolkits"
tags:
  - "Language documentation"
  - "OER"
  - "OpenSpeaks"
  - "Pronunciation"
  - "resources"
  - "Toolkit"
excerpt: "This is a part of OpenSpeaks toolkits library. See all the toolkits… Our pronunciation toolkit, Kathabhidhana is an open toolkit to record a large number of words. It consists of a few free/libre and open source software, open datasets, methodologies and documentations. It can be used to record pronunciations of words to make a talking […]"
embeds:
  - provider: "youtube"
    id: "UGMxwPtqDJY"
original_url: "https://theofdn.org/openspeaks/pronunciation/"
---
![OpenSpeaks logo (black)](/assets/logos/openspeaks.webp)

### This is a part of OpenSpeaks toolkits library. See all the [toolkits](/category/openspeaks/toolkit/)…

Our pronunciation toolkit, **Kathabhidhana** is an open toolkit to record a large number of words. It consists of a few free/libre and open source software, open datasets, methodologies and documentations. It can be used to record pronunciations of words to make a talking dictionary to record phonemes to create a text-to-speech software.

[[embed:0]]

**A tool with many faces**

Wikipedia has a sister project called Wiktionary, a multilingual dictionary where you can not just find meaning of words from your own language but also equivalent meanings of foreign language words. Unlike many available dictionaries that help learn pronunciations, Wiktionary does not have pronunciations of all words in all the languages. Kathabhidhana was originally started by Subhashish Panigrahi to add pronunciations to the Odia-language Wiktionary. It is adopted from a free software created by by Shrinivasan T. It works both on Linux and Mac. The iOS version of Kathabhidhana was created by Prateek Pattanaik. You can certainly create pronunciations and add them to Wiktionary. But you can use Kathabhidhana beyond that by making a large library of pronunciations that can be used to build any machine learning or Natural Language Processing (NLP) tool.

### What does this toolkit contain?

- A recording tool ([download for Linux/Mac and iOS](https://github.com/OdiaWikimedia/Kathabhidhana/archive/master.zip), [watch](https://www.youtube.com/watch?v=UGMxwPtqDJY) a video introduction to Kathabhidhana, [watch](https://www.youtube.com/watch?v=F-rmyZqKzrE&feature=youtu.be) a video tutorial for the iOS version)
- Instruction manual to set up the hardware and software (TBD)
- Dependency tools
  - Audacity for a post-recording batch clean up ([Download](http://www.audacityteam.org/download/), you can also check this tutorial in [English](https://www.youtube.com/watch?v=BPiYzFcRFMY), and [Odia](https://commons.wikimedia.org/wiki/File:How_to_make_vocals_more_clear_on_Audacity_%28Odia%29.webm "File:How to make vocals more clear on Audacity (Odia).webm") to clean up vocals for individual recordings)
  - [Pattypan](https://github.com/yarl/pattypan) for batch uploading recorded and edited audio files on Wikimedia Commons
- Open dataset: [CSV](https://docs.google.com/spreadsheets/d/1Vh08Dd6V743Q58ceCnNLc9BASaZQMAsGu1BOaa_dMQQ/pub?output=csv), [.ods](https://docs.google.com/spreadsheets/d/1Vh08Dd6V743Q58ceCnNLc9BASaZQMAsGu1BOaa_dMQQ/pub?output=ods) for reference while creating meta data for your recordings
- [Odia→International Phonetic Alphabet converter](https://or.wikipedia.org/s/14jk) (IPA)/Roman converter for adding phonetic signs in the metadata while uploading. Thiis converter works only the Odia alphabet. But you can fork and create one for your writing system too.

### Prerequisites

- Using a computer?
  - Linux or macOS
  - Linux running in a virtual machine
- Using an iOS device? (check more [here](https://github.com/pattaprateek/Kathabhidhana/tree/master/Kathabhidhana%20for%20iOS))
  - iOS (iPad or iPhone)
  - [Workflow](https://itunes.apple.com/us/app/workflow-powerful-automation-made-simple/id915249334?mt=8) (app)

### How to use it?

1.  Download and set up Kathabhidhana (see the next section)
2.  Set up your recording hardware (see mine in the picture above) e.g. microphone (if using an external one), computer settings like level
3.  Record using Kathabhidhana
4.  Batch processing using (tutorial coming soon, download Audacity from here)
5.  Manual clean up of each file (tutorial coming up soon)
6.  Setting up Pattypan and upload files on Commons (download from here)

### Installation

The installation can be done using command-line on a Linux or Mac computer, or using any iOS device.

Fork on [![GitHub Logo.png](/assets/logos/github.webp)](https://github.com/OdiaWikimedia/Kathabhidhana)

#### Linux

> `git clone `[`https://github.com/OdiaWikimedia/Kathabhidhana`](https://github.com/OdiaWikimedia/Kathabhidhana)
>
> `cd voice-recorder-for-tawictionary`
>
> `sh ./install.sh`

#### MacOS

> `git clone `[`https://github.com/OdiaWikimedia/Kathabhidhana`](https://github.com/OdiaWikimedia/Kathabhidhana)
>
> `cd Kathabhidhana`
>
> `ruby -e "$(curl -fsSL `[`https://raw.githubusercontent.com/Homebrew/install/master/install`](https://raw.githubusercontent.com/Homebrew/install/master/install)`)" < /dev/null 2> /dev/null`
>
> `brew install portaudio`
>
> `brew install vorbis-tools`
>
> `sudo easy_install pip`
>
> `sudo pip install pyaudio`

### Running the tool

1\. Go to the file called “file”. Replace all words with the words you want to record\
2. Run the command below (it will record both as .wav and .ogg)

> `python voice-record.py 2> err</code)`

[![`Running Kathabhidhana on MacOS.png`](/assets/images/pronunciation-running-on-macos.webp)](https://commons.wikimedia.org/wiki/File:Running_Kathabhidhana_on_MacOS.png)`3.`\
`Go to the path by using cd command in your terminal For instance, in my`\
`computer, it is the "Kathabhidhana" folder under "Documents". Then run:`

`python voice-record.py`

[![Recording words using Kathabhidhana command interface.png](/assets/images/pronunciation-recording-words.webp)](https://commons.wikimedia.org/wiki/File:Recording_words_using_Kathabhidhana_command_interface.png)The next steps are quite self-explanatory. You need to choose “Y” for yes and “N” for no in the following options inside your terminal.

To upload all the ogg files to Wikimedia Commons This will record the sounds in .ogg and .wav formats. You can then use a tool like [Pattypan](https://github.com/yarl/pattypan) to batch-upload either the .WAV or the .ogg files on Wikimedia Commons.

### Findings so far

[![Kathabhidhana - time spent for the entire process.gif](/assets/images/pronunciation-time-spent.webp)](https://commons.wikimedia.org/wiki/File:Kathabhidhana_-_time_spent_for_the_entire_process.gif)• It takes about 20-25 mins to record 100 words; A batch processing to convert and do overall auto-cleanup using Audacity will take about 5 mins for a 100-word-batch; It takes an average of 30 secs for 1 word to manually clean up, check quality, trim extra portions and other such editing work (meaning it will take about 45 mins to clean up a batch of 100 words) using Audacity; It takes about 5-10 mins for setting up Pattypan to upload the cleaned up words on Wikimedia Commons; On an average one would spend roughly about 1.5 hrs from recording to cleaning up to uploading for a batch of 100 words

## 

### Attribution

- Project led by Subhashish Panigrahi and the iOS tool is led by Prateek Pattanaik. All the media and text content are available under a CC-BY-SA 4.0 license
- All the software component is licensed under GNU General Public License (GPL) version 3 (read the License page for more details)
- This project and part of the documentation are based on the [Voice recorder](https://github.com/tshrinivasan/voice-recorder-for-tawictionary) for Tawiktionary project created by Shrinivasan T (please attribute Shrinivasan T if you’re making a derivative of the software)

### Blogs/media shoutouts

- Panigrahi, Subhashish. “[A simple command-line tool for recording audio](https://opensource.com/article/17/5/simple-command-line-tool-recording-audio)“. Opensource.com (May 12, 2017)
- Ojha, Bikash. Mishra, Chinmayee. Pattanaik, Prateek. Panigrahi, Subhashish. Patnaik, Sailesh. Elsharbaty, Samir. “[Community digest: As Odia Wikisource turns two, a project to digitize rare books kicks off; news in brief](https://blog.wikimedia.org/2017/03/30/digest-odia-wikisource/)“. Wikimedia Blog (March 30, 2017)
- Rezwan. “[A New Audio Uploading Tool for Crowdsourced Wiktionary Project in Odia Language](https://globalvoices.org/2017/02/12/a-new-audio-uploading-tool-for-crowdsourced-wiktionary-project-in-odia-language/)“. Global Voices (February 13, 2017)

### Talks/workshops

- “[Workshop “Kathabhidhana: Recording words for Wiktionary and preparing for an AI assistant](https://wikimania2017.wikimedia.org/wiki/Submissions/Kathabhidhana:_Recording_words_for_Wiktionary_and_preparing_for_an_AI_assistant)“. Wikimania 2017, Montreal, Canada. (*Selected for workshop on August 12. Check back in late August for more updates about the workshop*)
- “[Kathabhidhana, open source toolkit to record pronunciations of any world language](https://wikimedia.org.uk/wiki/Celtic_Knot_Conference_2017/Programme/CK129)“. Celtic Knot Conference 2017, University of Edinburgh. (*Selected, Workshop on July 6*)

### Some social media shout-outs:\
[Kathabhidhana](https://twitter.com/i/moments/898061810217213956)\
