# __Manzana Apple Music Tagger__

A python program to fetch credits info from apple music about albums, songs and music-videos and tag MP4 and M4A files using those credits info.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__light.png">
  <img alt="Apple Music" src="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__light.png">
</picture>

## __Features__

- Can tag an album or a single track or a music-video
- Embeds and saves artworks
- Saves animated artworks if available
- Saves time-synced lyrics if you have an Apple Music subscription
- Also tags the lyrics to the media file if available
- Adds newly released role-credits.

## __Required__

- [MP4Box](https://gpac.wp.imt.fr/downloads/)

## __How to use?__

### __# for all users__

First of all clone this project or download the project as a zip file and extract it to your pc. (or you can see [Releases](https://github.com/dropcreations/Manzana-Apple-Music-Tagger/releases))

```
git clone https://github.com/dropcreations/Manzana-Apple-Music-Tagger.git && cd Manzana-Apple-Music-Tagger
```

Install required modules for python (use `pip3` if `pip` doesn't work for you)

```
pip install -r requirements.txt
```

Then you have to ready your files for tagging. So, if you are tagging a complete album you must have the tracks in M4A format (with AAC or ALAC codec) and then rename each file as `01, 02, 03,...` (number must have 2-digits) respectively to the order of tracks in Apple Music. For an example, assume you have an album called __"Doja Cat - Planet Her"__ in __M4A__ format and they are currently renamed as below

```
Doja Cat - Planet Her (https://music.apple.com/us/album/planet-her/1573475827)
  │
  ├── Alone.m4a
  ├── Been Like This.m4a
  ├── Get Into It (Yuh).m4a
  ├── I Don't Do Drugs.m4a
  ├── Imagine.m4a
  ├── Kiss Me More.m4a
  ├── Love To Dream.m4a
  ├── Naked.m4a
  ├── Need to Know.m4a
  ├── Options.m4a
  ├── Payday.m4a
  ├── Women.m4a
  └── You Right.m4a
```

So, now you have to rename those as below.

```
Doja Cat - Planet Her (https://music.apple.com/us/album/planet-her/1573475827)
  │
  ├── Alone.m4a               as  12.m4a
  ├── Been Like This.m4a      as  09.m4a
  ├── Get Into It (Yuh).m4a   as  04.m4a
  ├── I Don't Do Drugs.m4a    as  06.m4a
  ├── Imagine.m4a             as  11.m4a
  ├── Kiss Me More.m4a        as  13.m4a
  ├── Love To Dream.m4a       as  07.m4a
  ├── Naked.m4a               as  02.m4a
  ├── Need to Know.m4a        as  05.m4a
  ├── Options.m4a             as  10.m4a
  ├── Payday.m4a              as  03.m4a
  ├── Women.m4a               as  01.m4a
  └── You Right.m4a           as  08.m4a
```

After renaming tracks, open terminal inside the folder that tracks included and run below command (Use `py` or `python3` if `python` doesn't work for you)

```
python manzana.py [album_url]
```

or if you are opening the terminal outside that folder, use below command

```
python manzana.py --input [folder_path] [album_url]
```

If you are tagging a single file, don't need to rename it. just use below command

```
python manzana.py --input [file_path] [song_url]
```

If you want to get animated cover if available, use `--animartwork` or `-an` argument

```
python manzana.py -an [album or song url]
```

Get help using `-h` or `--help` command

```
usage: manzana.py [-h] [-v] [-sc {2,3}] [-an] [-cn] [-ln] [-sv] [-i INPUT] url

Manzana: Apple Music Tagger

positional arguments:
  url                   Apple Music URL

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -sc {2,3}, --sync {2,3}
                        Timecode's ms point count in synced lyrics. (default: 2)
  -an, --animartwork    Download the animated artwork if available. (default: False)
  -cn, --no-cover       Don't save album artwork. (default: False)
  -ln, --no-lrc         Don't save time-synced lyrics as a .lrc file. (default: False)
  -sv, --skip-video     Skip videos in an album. (default: False)
  -i INPUT, --input INPUT
                        Folder or file path for m4a/mp4 media files. (default: Current working directory)
```

### __# for subscribed users__

Get your Apple Music cookies from web browser and search for `media-user-token` and get it.

|Domain|Include subdomains|Path|Secure|Expiry|Name|Value
|---|---|---|---|---|---|---|
|.apple.com|TRUE|/|FALSE|0|geo|##|
|.apple.com|TRUE|/|TRUE|0|dslang|##-##|
|.apple.com|TRUE|/|TRUE|0|site|###|
|.apple.com|TRUE|/|TRUE|0|myacinfo|#####...|
|.music.apple.com|TRUE|/|TRUE|1680758167|commerce-authorization-token|#####...|
|.apple.com|TRUE|/|FALSE|1715317057|itspod|##|
|.music.apple.com|TRUE|/|TRUE|1681361859|media-user-token|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|itre|#|
|.music.apple.com|TRUE|/|TRUE|1681361859|pldfltcid|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|pltvcid|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|itua|##|

You need to add `mediaUserToken` to get `lyricist` and `lyrics` and also to save `timeSyncedLyrics` as a `.lrc` file.<br>
Program will ask you for the `mediaUserToken` when you run it. If you don't want to use subscription, you can skip that by hitting `Enter` key.
If you want to use subscription, run below command to clear the configuration and run the program again.

```
python manzana.py reset
```

When saving time synced lyrics, timestamps are in `00:00.00` format. If you want to get it in `00:00.000` format set `--sync` as `3` as below

```
python manzana.py --sync 3 [album or song url]
```

If you don't want to get time synced lyrics as `.lrc` file, use `--no-lrc` argument.

```
python manzana.py --no-lrc [album or song url]
```

If you don't want to use your subscription anymore use below command again to reset and skip when it ask for `mediaUserToken`.

```
python manzana.py reset
```

### Sample

```
Format                      : MPEG-4
Format profile              : Apple audio with iTunes info
Codec ID                    : M4A  (isom/M4A /mp42)
File size                   : 9.12 MiB
Duration                    : 2 min 54 s
Overall bit rate mode       : Variable
Overall bit rate            : 438 kb/s
Album                       : AUSTIN
Album/Performer             : Post Malone
Part/Position               : 1
Part/Total                  : 1
Track name                  : Something Real
Track name/Position         : 2
Track name/Total            : 17
Performer                   : Post Malone
Composer                    : Post Malone / Louis Bell / Andrew Watt / Billy Walsh
Lyricist                    : Andrew Watt / Billy Walsh / Louis Bell / Post Malone
Producer                    : Post Malone / Louis Bell / Andrew Watt
Label                       : Mercury Records/Republic Records
Genre                       : Pop / Music
ContentType                 : Music
Recorded date               : 2023-07-28
Encoded date                : 2023-06-16 04:29:22 UTC
Tagged date                 : 2023-06-16 04:29:22 UTC
ISRC                        : USUM72306013
Copyright                   : ℗ 2023 Mercury Records/Republic Records, a division of UMG Recordings, Inc.
Cover                       : Yes
Lyrics                      : Gimme something I can feel / Light a cigarette just so I can breathe / Gimme something, something real / Seven hundred feet off the coast of Greece / Gimme something I can feel / No reservation, pull up twenty deep / Gimme something, something real / I would trade it all just to be at peace / Stop, the gear's too high, this is overload / It don't matter what car is sittin' outside, it's a lonely road / It's a double-edged sword, cuttin' off ties with the ones I know / So tell me, how the fuck am I still alive? It's a miracle / And I can't believe, ran through a B at Louis V / It's what I need right now / It's just my need, at the gates of hell, no VIP / Everybody waits in line / So gimme something I can feel / 720S, 750 V / Gimme something, something real / I was in Maldives, sippin' burgundy / Gimme something I can feel / Prada on my dick, Prada on my sleeve / Gimme something, something real / I could play that pussy like it's "Für Elise" / I got real habits, I'm a snowmobile addict / Teal Patek steel when I feel panic / Throw a mil' at it, problem, throw a bill at it / Still at it, sign-another-deal addict / And I can't believe everybody gets to drink for free / So give me one more round / No cover fee at the gates of hell, no VIP / Everybody waits in line / So gimme something I can feel / Light a cigarette just so I can breathe / Gimme something, something real / How much psilocybin can a human eat? / Gimme something I can feel / Whiskey lullaby just to fall asleep / Gimme something, something real / And it's what I want, it ain't what I need / Gimme something I can feel / Got everything, guess I'm hard to please / Gimme something, something real / I would trade my life just to be at peace / Gimme something I can feel / Gimme something, something real
Rating                      : Explicit
Keyboards                   : Louis Bell
Piano                       : Louis Bell
Programming                 : Louis Bell
Mastering Engineer          : Mike Bozzi
Drums                       : Andrew Watt
Choir Arranger              : Andrew Watt
Lead Vocals                 : Post Malone
Mixing Engineer             : Spike Stent
UPC                         : 00602455789501
Guitar                      : Post Malone / Andrew Watt
Recording Engineer          : Marco Sonzini / Paul Lamalfa
Songwriter                  : Louis Bell / Austin Post / Andrew Watt / Billy Walsh
Assistant Recording Enginee : Jed Jones / Joe Dougherty / Tommy Turner / Braden Bursteen
Choir                       : James Connor / Alexandria Griffin / Amanda Adams / Anthony Jawan / Brooke Brewer / Carl Foster / Chelsea West / Dwanna Orange / Herman Bryant III / Jajuan Glasper / Jasmine Patton / Jason White / Jerel Duren / JeRonelle McGhee / Kristin-Ilycia Lowe / Lanita Smith / Michael Adkins / Nelle Rose / Nikisha Grier / Ashly Williams / Carmel Echols / George Hamilton / Chelsea Miller / Jason McGee / Cassandra Chism / Natalie LaFourche / Tiffany Commons / Teresa Davis / Taneka Lemle / Brianna Lankford / Anthony Johnson / Zachary Moore / Vernon Burris / Michael Essex / Derrick Jenkins / Marquee Perkins / Camille Grigsby / Nicole Stevens / Quishima Dixon / Skyler Pugh / Shannon Pierre / Corinthian Buffington / Phylicia Hill
```

## About me

Hi, You might recognize me as GitHub's [dropcreations](https://github.com/dropcreations).

__Other useful python scripts done by me__

| Project        | Github location                                |
|----------------|------------------------------------------------|
| mkvextractor   | https://github.com/dropcreations/mkvextractor  |
| flactagger     | https://github.com/dropcreations/flactagger    |
| mp4tagger      | https://github.com/dropcreations/mp4tagger     |
| mkvtagger      | https://github.com/dropcreations/mkvtagger     |

<br>

- __NOTE: If you found any issue using this program, mention in issues section__

## Support

[!["Buy Me A Coffee"](https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0)](https://ko-fi.com/dropcodes)
