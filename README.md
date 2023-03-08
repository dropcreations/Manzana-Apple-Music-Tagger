# __Apple-Music-Tagger__

A python script to fetch credits info from apple music about albums and songs and tag FLAC and M4A files using those credits info.

<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dropcreations/Apple-Music-Tagger/main/Assets/logo-in-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dropcreations/Apple-Music-Tagger/main/Assets/logo-in-light.png">
<img alt="Apple Music" src="https://raw.githubusercontent.com/dropcreations/Apple-Music-Tagger/main/Assets/logo-in-light.png">
</picture>

## __Features__

- Can tag an album or a single track
- Tags and saves artworks
- Saves time-synced lyrics if you have an Apple Music subscription
- Also tags the lyrics to the media file if available

## __How to use?__

### __# for all users__

First of all clone this projector download the project as a zip file and extract it to your pc.

```
git clone https://github.com/dropcreations/Apple-Music-Tagger.git && cd Apple-Music-Tagger
```

Install required modules for python (use `pip3` if `pip` doesn't work for you)

```
pip install -r requirements.txt
```

You have to ready your files for tagging. So, if you are tagging a complete album you must have the tracks in FLAC or M4A format and then rename each file as `1, 2, 3,...` respectively to the order of tracks in Apple Music. For an example, assume you have an album called __"Doja Cat - Planet Her"__ in __FLAC__ format and they are currently renamed as below

```
Doja Cat - Planet Her (https://music.apple.com/us/album/planet-her/1573475827)
  |
  |--Alone.flac               as  12.flac
  |--Been Like This.flac      as  9.flac
  |--Get Into It (Yuh).flac   as  4.flac
  |--I Don't Do Drugs.flac    as  6.flac
  |--Imagine.flac             as  11.flac
  |--Kiss Me More.flac        as  13.flac
  |--Love To Dream.flac       as  7.flac
  |--Naked.flac               as  2.flac
  |--Need to Know.flac        as  5.flac
  |--Options.flac             as  10.flac
  |--Payday.flac              as  3.flac
  |--Women.flac               as  1.flac
  |--You Right.flac           as  8.flac
```

After renaming tracks, open terminal inside the folder that tracks included and run below command (Use `py` or `python3` if `python` doesn't work for you)

```
python apple-tagger.py [album_url]
```

or if you are opening the terminal outside that folder, use below command

```
python apple-tagger.py --dir [folder_path] [album_url]
```

if you are tagging a single file, don't need to rename it. just use below command

```
python apple-tagger.py --file [file_path] [song_url]
```

Get help using `-h` or `--help` command

```
usage: apple-tagger.py [-h] [-d DIR] [-f FILE] url

Tag FLAC/M4A media files using Apple Music's credit info

positional arguments:
  url                   url from Apple Music for a album or a track

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     folder path where media files contains for whole album tagging
  -f FILE, --file FILE  audio file path for single track tagging
```

### __# for subscribed users__

Get your `media-user-token` from web browser and paste it in `settings.json` file

```
{
    "media-user-token": ""
}
```

You need to add `media-user-token` to get `lyricist` and `lyrics` and also to save `time-synced-lyrics` as a `.lrc` file.


## About me

Hi, I'm Dinitha. You might recognize me as GitHub's [dropcreations](https://github.com/dropcreations).

__Other usefull python scripts done by me__

| Project        | Github location                                |
|----------------|------------------------------------------------|
| MKVExtractor   | https://github.com/dropcreations/MKVExtractor  |
| FLAC-Tagger    | https://github.com/dropcreations/FLAC-Tagger   |
| MP4/M4A-Tagger | https://github.com/dropcreations/MP4-Tagger    |
| MKV-Tagger     | https://github.com/dropcreations/MKV-Tagger    |

<br>

- __NOTE: If you found any issue using this script mention in issues section__
