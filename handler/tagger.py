import os

from mutagen.mp4 import MP4, MP4Cover
from sanitize_filename import sanitize

from utils import Logger

logger = Logger("Handler")

def tag(media, data, nocover=False, nolrc=False, mediaUserToken=False):
    if data.get("type") == 1: name = str(data.get("tracknumber")).zfill(2) + ' - ' + data.get("track")
    else: name = data.get("trackartist") + ' - ' + data.get("track")

    tags = MP4(media)
    tags.delete()

    rating = 0
    if data.get("rating") == "explicit":
        rating = 4

    __tags = {
        "\xa9alb": data.get("album"),
        "\xa9nam": data.get("track"),
        "aART": data.get("albumartist"),
        "\xa9ART": data.get("trackartist"),
        "\xa9wrt": data.get("composer"),
        "\xa9gen": data.get("genre"),
        "rtng": rating,
        "\xa9day": data.get("releasedate"),
        "cprt": data.get("copyright"),
        "stik": data.get("type"),
        "\xa9lyr": data.get("lyrics"),
        "trkn": (data.get("tracknumber"), data.get("trackcount")),
        "disk": (data.get("discnumber"), data.get("discnumber")),
        "----:com.apple.itunes:Label": data.get("recordlabel"),
        "----:com.apple.itunes:ISRC": data.get("isrc"),
        "----:com.apple.itunes:UPC": data.get("upc"),
        "----:com.apple.itunes:Lyricist": data.get("songwriter"),
    }

    if data.get("type") == 6:
        del __tags["trkn"]
        del __tags["disk"]

    for key, value in __tags.items():
        if value:
            if key.startswith("----:com.apple.itunes:"): value = value.encode()
            if isinstance(value, list): tags[key] = value
            else: tags[key] = [value]

    if data.get("type") == 1:
        if not nocover:
            logger.info("Embedding artwork...")
            tags["covr"] = [MP4Cover(open("Cover.jpg", 'rb').read(), MP4Cover.FORMAT_JPEG)]

        if not nolrc:
            if mediaUserToken:
                if "timeSyncedLyrics" in data:
                    logger.info("Saving time-synced lyrics...")
                    with open(f"{name}.lrc", "w", encoding="utf-8") as l:
                        l.write('\n'.join(data.get("timeSyncedLyrics")))
                else: logger.warning("Unable to find time-synced lyrics!")
            
    
    logger.info("Tagging media file...")
    tags.save()

    if data.get("type") == 1:
        logger.info(f'Re-naming "{os.path.basename(media)}" ──> "{name}.m4a"')
        os.rename(media, sanitize(f"{name}.m4a"))
    else:
        logger.info(f'Re-naming "{os.path.basename(media)}" ──> "{name}.mp4"')
        os.rename(media, sanitize(f"{name}.mp4"))