import os
import m3u8
import json

from rich import box
from rich.table import Table
from rich.console import Console
from rich.columns import Columns
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from utils import Logger

console = Console()
logger = Logger("Handler")
    
def checkUrl(url):
    try:
        urlopen(url)
        return True
    except (URLError, HTTPError):
        return False
    
def getFiles(path):
    logger.info("Getting files ready...")
    path = os.path.realpath(path)

    if os.path.isdir(path):
        content = os.listdir(path)
        content = [os.path.join(path, file) for file in content if os.path.splitext(file)[1] in [".mp4", ".m4a"]]

        if os.path.join(path, "Cover.mp4") in content:
            content.remove(os.path.join(path, "Cover.mp4"))
        if len(content) == 0: logger.error("Input folder has no any supported file!", 1)
    else:
        if os.path.splitext(path)[1] in [".mp4", ".m4a"]: content = [path]
        else: logger.error("Input file is not supported!", 1)

    return content

def __getInitUri(m3u8Uri):
    data = m3u8.load(m3u8Uri)
    baseUri = data.base_uri
    data = json.loads(json.dumps(data.data))
    return baseUri + data["segment_map"][0]["uri"]

def getAnimated(data):
    if "animartwork" in data:
        logger.info("Getting animated artwork streams list...")

        ids = []
        streamList = data.get("animartwork")

        table = Table(box=box.ROUNDED)

        table.add_column("ID", justify="center")
        table.add_column("Codec", justify="center")
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
        columns = Columns(["       ", table])
        console.print(columns)
        id = int(input("\n\t Enter ID: "))
        print()

        if id in ids: return [__getInitUri(streamList[id].get("uri")), streamList[id].get('resolution')]
        else: logger.error("ID not found in the list!", 1)
    else: logger.error("No animated artworks available!")