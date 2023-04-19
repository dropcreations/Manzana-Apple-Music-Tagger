import os
from loggings import Logger
from mutagen.mp4 import MP4, MP4Cover

logger = Logger("FileTagger")

def save_synced_lyrics(lyrics, lrc):
    logger.info("Saving time-synced lyrics...")
    with open(lrc, "w", encoding="UTF-8") as l:
        l.write("\n".join(lyrics))

def tag(file, info, coverFile, noSync=False):
    tagger = MP4(file)
    tagger.delete()
    logger.info("Tagging media file...")

    if "albumName" in info:
        album_name = info.get("albumName")
        if " - Single" in album_name: album_name = album_name.replace(" - Single", "")
        elif " - EP" in album_name: album_name = album_name.replace(" - EP", "")
        tagger['\xa9alb'] = [album_name]
    if "trackName" in info: tagger['\xa9nam'] = [info.get("trackName")]
    if "albumArtist" in info: tagger['aART'] = [", ".join(info.get("albumArtist"))]
    if "trackArtist" in info: tagger['\xa9ART'] = [", ".join(info.get("trackArtist"))]
    if "composer" in info: tagger['\xa9wrt'] = info.get("composer")
    if "genre" in info: tagger['\xa9gen'] = [", ".join(info.get("genre"))]
    if "rating" in info:
        if info.get("rating") == "explicit": tagger['rtng'] = [4]
    if "releaseDate" in info: tagger['\xa9day'] = [info.get("releaseDate")]
    if "trackNumber" in info: tagger['trkn'] = [(int(info.get("trackNumber")), int(info.get("trackCount")))]
    if "discNumber" in info: tagger['disk'] = [(int(info.get("discNumber")), int(info.get("discNumber")))]
    if "recordLabel" in info: tagger['----:com.apple.itunes:Label'] = [info.get("recordLabel").encode()]
    if "copyright" in info: tagger['cprt'] = [info.get("copyright")]
    if "isrc" in info: tagger['----:com.apple.itunes:ISRC'] = [info.get("isrc").encode()]
    if "upc" in info: tagger['----:com.apple.itunes:UPC'] = [info.get("upc").encode()]
    if "songwriters" in info: tagger['----:com.apple.itunes:Lyricist'] = [", ".join(info.get("songwriters")).encode()]
    if "lyrics" in info: tagger['\xa9lyr'] = info.get("lyrics")

    if info.get("type") == "song":
        logger.info("Embedding cover...")
        if os.path.splitext(coverFile)[1] == ".jpg":
            tagger['covr'] = [MP4Cover(open(coverFile, 'rb').read(), MP4Cover.FORMAT_JPEG)]
        elif os.path.splitext(coverFile)[1] == ".png":
            tagger['covr'] = [MP4Cover(open(coverFile, 'rb').read(), MP4Cover.FORMAT_PNG)]
        tagger['stik'] = [1]
    else:
        tagger['stik'] = [6]
    tagger.save()
    
    if info.get("type") == "song":
        track_no = str(info.get("trackNumber")).zfill(2)
        track_name = info.get("trackName")
        logger.info(f'Renaming "{file}" ──> "{track_no} - {track_name}.m4a"...')
        os.rename(file, f"{track_no} - {track_name}.m4a")
        if not noSync:
            if "timeSyncedLyrics" in info: save_synced_lyrics(info.get("timeSyncedLyrics"), f"{track_no} - {track_name}.lrc")
            else: logger.warning("No time-synced lyrics found!")
    elif info.get("type") == "music-video":
        track_artist = ", ".join(info.get("trackArtist"))
        track_name = info.get("trackName")
        os.rename(file, f"{track_artist} - {track_name}.mp4")