import os
import requests
import subprocess
from utils import Logger
from rich.table import Table
from rich.console import Console
from rich.traceback import install

install()

console = Console()
logger = Logger("Manzana")

def yt_dlp(url, output):
    return subprocess.Popen(["yt-dlp", "-q",
                             "--no-warnings",
                             "--allow-unplayable",
                             "-o", output, url],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT).wait()

def muxhls(input):
    return subprocess.Popen(["mp4box", "-add", input,
                             "-new", f"_{input}"],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT).wait()

def getFiles(path):
    logger.info("Getting files...")
    if path == "current": path = os.getcwd()

    if os.path.isdir(path):
        os.chdir(path)

        content = os.listdir(os.getcwd())
        content = [file for file in content if os.path.splitext(file)[1] in [".mp4", ".m4a"]]

        if "Cover.mp4" in content: content.remove("Cover.mp4")
        if len(content) == 0: logger.error("Input folder has no any supported file!", 1)
    else:
        if os.path.splitext(path)[1] in [".mp4", ".m4a"]:
            os.chdir(os.path.dirname(os.path.realpath(path)))
            content = [path]
        else: logger.error("Input file is not supported!", 1)

    return content

def getOriginal(coverUrl):
    logger.info("Getting uncompressed original artwork...")
    image_formats = ("image/png", "image/jpeg", "image/jpg")

    original = "https://a1.mzstatic.com/r40/" + '/'.join(coverUrl.split('/')[5:-1])
    response = requests.head(original)

    if response.headers["content-type"] in image_formats:
        ext = os.path.splitext(original)[1]
        return [original, f"Cover{ext}"]
    else:
        logger.error("Unable to parse original artwork url!")
        return None
    
def getAnimated(data):
    if not os.path.exists("Cover.mp4"):
        if "animatedCover" in data:
            logger.info("Getting animated video artwork streams list...")

            ids = []
            streamList = data.get("animatedCover")

            table = Table(show_header=True)

            table.add_column("ID", justify="center")
            table.add_column("Codec", justify="left")
            table.add_column("Bitrate", justify="left")
            table.add_column("Resolution", justify="left")
            table.add_column("FPS", justify="center")
            table.add_column("Range", justify="center")

            for stream in streamList:
                ids.append(stream.get("id"))
                table.add_row(
                    str(stream.get("id")),
                    stream.get("codec"),
                    stream.get("bitrate"),
                    stream.get("resolution"),
                    str(stream.get("fps")),
                    stream.get("range")
                )
            
            print()
            console.print(table)

            id = int(input("\nEnter ID: "))
            print()

            if id in ids:
                logger.info(f"Downloading {streamList[id].get('resolution')}px animated artwork...")

                if yt_dlp(streamList[id].get("uri"), "Cover.mp4") == 0:
                    logger.info("Muxing animated artwork...")

                    if muxhls("Cover.mp4") == 0:
                        os.remove("Cover.mp4")
                        os.rename("_Cover.mp4", "Cover.mp4")
                    else: logger.warning("Muxing failed! Ignoring animated artwork...")
                else: logger.warning("Download failed! Ignoring animated artwork...")
            else: logger.error("ID not found in the list!", 1)
        else: logger.error("No animated artworks available!")
    else: logger.warning("Animated artwork 'Cover.mp4' already exists! Ignoring...")