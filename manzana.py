import os
import argparse
import subprocess
from tagger import tag
from loggings import Logger
from applemusic import AppleMusic
from prettytable import PrettyTable

logger = Logger("Downloader")

LOGO = """


                 ███╗   ███╗ █████╗ ███╗   ██╗███████╗ █████╗ ███╗   ██╗ █████╗ 
                 ████╗ ████║██╔══██╗████╗  ██║╚══███╔╝██╔══██╗████╗  ██║██╔══██╗
                 ██╔████╔██║███████║██╔██╗ ██║  ███╔╝ ███████║██╔██╗ ██║███████║
                 ██║╚██╔╝██║██╔══██║██║╚██╗██║ ███╔╝  ██╔══██║██║╚██╗██║██╔══██║
                 ██║ ╚═╝ ██║██║  ██║██║ ╚████║███████╗██║  ██║██║ ╚████║██║  ██║
                 ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                                  ──── Apple Music Tagger ────                 


"""

def process_media(path):
    logger.info("Proccessing media...")
    if path == "console":
        path = os.getcwd()
    if os.path.isdir(path):
        os.chdir(path)
        content = os.listdir(os.getcwd())
        content = [file for file in content if os.path.splitext(file)[1] in [".mp4", ".m4a"]]
        if "Cover.mp4" in content: content.remove("Cover.mp4")
        if len(content) == 0: logger.error("Input folder has no any supported file!", 1)
    else:
        if os.path.splitext(path)[1] in [".mp4", ".m4a"]:
            os.chdir(os.path.dirname(os.path.abspath(path)))
            content = [path]
        else: logger.error("Input file is not supported!", 1)

    return content

def __download(url, output):
    return subprocess.Popen(["yt-dlp",
                             "-q",
                             "--no-warnings",
                             "--allow-unplayable",
                             "-o",
                             output,
                             url],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT).wait()

def __mux(_input):
    return subprocess.Popen(["mp4box",
                             "-add",
                             _input,
                             "-new",
                             f"_{_input}"],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT).wait()

def download_artwork(info):
    if os.path.exists("Cover.png"): os.remove("Cover.png")
    if os.path.exists("Cover.jpg"): os.remove("Cover.jpg")

    embed_cover = info["embedCover"]["compressedUrl"].get("jpg")
    if "externalCover" in info:
        if info["externalCover"].get("originalUrl") is not None:
            external_cover = info["externalCover"].get("originalUrl")
        else:
            if info["externalCover"]["compressedUrl"].get("png") is not None:
                external_cover = info["externalCover"]["compressedUrl"].get("png")
            else:
                external_cover = info["externalCover"]["compressedUrl"].get("jpg")
    else:
        if info["embedCover"].get("originalUrl") is not None:
            external_cover = info["embedCover"].get("originalUrl")
        else:
           external_cover = info["embedCover"]["compressedUrl"].get("png")

    logger.info("Downloading artworks...")

    if not os.path.exists("externalCover.png") or not os.path.exists("externalCover.jpg"):
        __download(external_cover, f"externalCover{os.path.splitext(external_cover)[1]}")
    if not os.path.exists("embedCover.png") or not os.path.exists("embedCover.jpg"):
        __download(embed_cover, f"embedCover{os.path.splitext(embed_cover)[1]}")

    return [
        f"externalCover{os.path.splitext(external_cover)[1]}",
        f"embedCover{os.path.splitext(embed_cover)[1]}"
    ]

def download_animated_artwork(info):
    if not os.path.exists("Cover.mp4"):
        logger.info("Getting animated video artworks list...")
        if "animatedCover" in info:
            an_square = info.get("animatedCover")
            ids = []

            table = PrettyTable()
            table.field_names = [" ID ", "Codec", "Bitrate", "Resolution", "FPS", "Range"]

            table.align[" ID "] = "c"
            table.align["Codec"] = "c"
            table.align["Bitrate"] = "l"
            table.align["Resolution"] = "l"
            table.align["FPS"] = "c"
            table.align["Range"] = "c"

            for stream in an_square:
                ids.append(stream.get("id"))
                table.add_row([stream.get("id"),
                            stream.get("codec"),
                            stream.get("bitrate"),
                            stream.get("resolution"),
                            stream.get("fps"),
                            stream.get("range")])

            table = str(table)
            table = table.replace("\n", "\n\t")
            print(f'\n\t{table}')

            _id = int(input("\n\tEnter ID: "))
            print()
            if _id in ids:
                logger.info(f"Downloading {an_square[_id].get('resolution')} animated artwork...")
                if __download(an_square[_id].get("uri"), "Cover.mp4") == 0:
                    logger.info("Muxing animated artwork...")
                    if __mux("Cover.mp4") == 0:
                        os.remove("Cover.mp4")
                        os.rename("_Cover.mp4", "Cover.mp4")
                    else: logger.warning("Muxing failed! Ignoring animated artwork...")
                else: logger.warning("Download failed! Ignoring animated artwork...")
            else: logger.error("ID not found in the list!", 1)
        else: logger.error("No animated artworks available!")
    else: logger.error("Animated artwork already exists!")

def main():
    parser = argparse.ArgumentParser(
        description="Manzana: Apple Music albums, songs, music-videos tagger"
    )
    parser.add_argument(
        '-sp',
        '--sync-points',
        choices=[2, 3],
        default=3,
        help="Miliseconds point count in synced lyrics",
    )
    parser.add_argument(
        '-an',
        '--animated',
        help="Download the animated artwork if available",
        action="store_true",
    )
    parser.add_argument(
        '-cn',
        '--no-cache',
        help="Don't look for cache",
        action="store_true",
    )
    parser.add_argument(
        '-ln',
        '--no-sync-lrc',
        help="Don't save synced lyrics as a '.lrc'",
        action="store_true",
    )
    parser.add_argument(
        '-p',
        '--path',
        help="Folder or file path for media",
        default="console",
    )
    parser.add_argument(
        'url',
        help="url from Apple Music for a album, song or music-video",
        type=str
    )
    args = parser.parse_args()

    media = process_media(args.path)

    applemusic = AppleMusic(syncPoints=args.sync_points, noCache=args.no_cache)
    data = applemusic.get_info(args.url)

    cover = download_artwork(data)
    if args.animated: download_animated_artwork(data)

    for i, file in enumerate(media):
        tag(file, data["tracks"][i], cover[1], args.no_sync_lrc)

    os.remove(cover[1])
    os.rename(cover[0], f"Cover{os.path.splitext(cover[0])[1]}")
    logger.info("Successfully completed.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)
    main()