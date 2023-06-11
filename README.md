# __Manzana-Apple-Music-Tagger__

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

## __Required__

- [mp4box](https://gpac.wp.imt.fr/downloads/)

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
python manzana.py --path [folder_path] [album_url]
```

If you are tagging a single file, don't need to rename it. just use below command

```
python manzana.py --path [file_path] [song_url]
```

If you want to get animated cover if available, use `--animated` or `-an` argument

```
python manzana.py -an [album or song url]
```

Get help using `-h` or `--help` command

```
usage: manzana.py [-h] [-sc {2,3}] [-an] [--no-cover] [--no-lrc] [-p PATH] url

Manzana: Apple Music Tagger

positional arguments:
  url                           Apple Music URL

optional arguments:
  -h, --help                    show this help message and exit
  -sc {2,3}, --sync {2,3}       Timecode's ms point count in synced lyrics
  -an, --animated               Download the animated artwork if available
  --no-cover                    Don't save album artwork
  --no-lrc                      Don't save time-synced lyrics as a .lrc file
  -p PATH, --path PATH          Folder or file path for m4a/mp4 media
```

### __# for subscribed users__

Get your Apple Music cookies from web browser and search for `media-user-token` and get it.

```
.apple.com	      TRUE	/	FALSE	0	          geo	                          ##
.apple.com	      TRUE	/	TRUE	0	          dslang	                      ##-##
.apple.com	      TRUE	/	TRUE	0	          site	                        ###
.apple.com	      TRUE	/	TRUE	0	          myacinfo	                    #####...
.music.apple.com	TRUE	/	TRUE	1680758167	commerce-authorization-token	#####...
.apple.com	      TRUE	/	FALSE	1715317057	itspod	                      ##
.music.apple.com	TRUE	/	TRUE	1681361859	media-user-token	            #####...
.music.apple.com	TRUE	/	TRUE	1681361859	itre	                        #
.music.apple.com	TRUE	/	TRUE	1681361859	pldfltcid	                    #####...
.music.apple.com	TRUE	/	TRUE	1681361859	pltvcid	                      #####...
.music.apple.com	TRUE	/	TRUE	1681361859	itua	                        ##
```

You need to add `media-user-token` to get `lyricist` and `lyrics` and also to save `time-synced-lyrics` as a `.lrc` file.<br>
Now you have to run `init` command to enter `media-user-token`.

```
python manzana.py init
```

When saving time synced lyrics, timestamps are in `00:00.000` format. If you want to get it in `00:00.00` format set `--sync` as `2` as below

```
python manzana.py --sync 2 [album or song url]
```

If you don't want to get time synced lyrics as `.lrc` file, use `--no-lrc` argument.

```
python manzana.py --no-lrc [album or song url]
```

If you don't want to use your `media-user-token` use below command to reset.

```
python manzana.py reset
```

## About me

Hi, You might recognize me as GitHub's [dropcreations](https://github.com/dropcreations).

__Other useful python scripts done by me__

| Project        | Github location                                |
|----------------|------------------------------------------------|
| MKVExtractor   | https://github.com/dropcreations/MKVExtractor  |
| FLAC-Tagger    | https://github.com/dropcreations/FLAC-Tagger   |
| MP4/M4A-Tagger | https://github.com/dropcreations/MP4-Tagger    |
| MKV-Tagger     | https://github.com/dropcreations/MKV-Tagger    |

<br>

- __NOTE: If you found any issue using this program, mention in issues section__
