import m3u8
import json

from rich import box
from rich.table import Table
from rich.console import Console
from rich.columns import Columns

from utils import logger

console = Console()

def __getUri(uri):
    data = m3u8.load(uri)
    baseUri = data.base_uri
    data = json.loads(
        json.dumps(
            data.data
        )
    )

    return baseUri + data["segment_map"][0]["uri"]

def animartwork(streamList):
    logger.info("Getting animated artwork streams list...")

    ids = []

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

    if id in ids:
        return [
            __getUri(streamList[id].get("uri")),
            streamList[id].get('resolution')
        ]
    else:
        logger.error("ID not found in the list!", 1)