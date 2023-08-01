import os

from mutagen.mp4 import MP4, MP4Cover
from sanitize_filename import sanitize

from utils import logger

def tag(
    media,
    data,
    nocover=False,
    nolrc=False,
    mediaUserToken=False
):
    if data["type"] == 1:
        name = str(data["trackno"]).zfill(2) + ' - ' + data["song"]
    else:
        name = data["songartist"] + ' - ' + data["song"]

    tags = MP4(media)
    tags.delete()

    rating = 0
    if "rating" in data:
        if data["rating"] == "explicit":
            rating = 4

    __tags = {
        "\xa9alb": data.get("album"),
        "\xa9nam": data.get("song"),
        "aART": data.get("albumartist"),
        "\xa9ART": data.get("songartist"),
        "\xa9wrt": data.get("composer"),
        "\xa9gen": data.get("genre"),
        "rtng": rating,
        "\xa9day": data.get("releasedate"),
        "cprt": data.get("copyright"),
        "stik": data.get("type"),
        "\xa9lyr": data.get("lyrics"),
        "trkn": (data.get("trackno"), data.get("trackcount")),
        "disk": (data.get("discno"), data.get("discno")),
        "----:com.apple.itunes:Label": data.get("recordlabel"),
        "----:com.apple.itunes:ISRC": data.get("isrc"),
        "----:com.apple.itunes:UPC": data.get("upc"),
        "----:com.apple.itunes:Lyricist": data.get("songwriter"),
    }

    if "credits" in data:
        for k, v in data["credits"].items():
            __tags[f'----:com.apple.itunes:{k}'] = v

    if data["type"] == 6:
        del __tags["trkn"]
        del __tags["disk"]

    for key, value in __tags.items():
        if value:
            if isinstance(value, list):
                value = ['\r\n'.join(value)]
                
                if key.startswith("----:com.apple.itunes:"):
                    value = [val.encode() for val in value]

                tags[key] = value
            else:
                if key.startswith("----:com.apple.itunes:"):
                    value = value.encode()
                
                if key in [
                    "aART",
                    "\xa9ART",
                    "\xa9wrt",
                    "\xa9lyr",
                    "----:com.apple.itunes:Lyricist"
                ]:
                    value = value.replace(
                        ', ',
                        '\r\n'
                    ).replace(
                        ' & ',
                        '\r\n'
                    )

                tags[key] = [value]

    if data["type"] == 1:
        if not nocover:
            logger.info("Embedding artwork...")
            tags["covr"] = [MP4Cover(open("Cover.jpg", 'rb').read(), MP4Cover.FORMAT_JPEG)]

        if not nolrc:
            if mediaUserToken:
                if "timeSyncedLyrics" in data:
                    logger.info("Saving time-synced lyrics...")

                    with open(sanitize(f"{name}.lrc"), "w", encoding="utf-8") as l:
                        l.write(
                            '\n'.join(
                                data["timeSyncedLyrics"]
                            )
                        )
                else:
                    logger.warning("Unable to find time-synced lyrics!")
            
    
    logger.info("Tagging media file...")
    tags.save()

    if data["type"] == 1:
        logger.info(f'Re-naming "{os.path.basename(media)}" ──> "{name}.m4a"')
        try: os.rename(media, sanitize(f"{name}.m4a"))
        except FileExistsError: pass
    else:
        logger.info(f'Re-naming "{os.path.basename(media)}" ──> "{name}.mp4"')
        try: os.rename(media, sanitize(f"{name}.mp4"))
        except FileExistsError: pass