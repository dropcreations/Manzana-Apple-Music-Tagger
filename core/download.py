import os
import signal
import aiohttp
import asyncio

from threading import Event
from functools import partial
from urllib.request import urlopen

from utils import logger

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)

doneEvent = Event()

def handleSigint(signum, frame):
    doneEvent.set()

signal.signal(signal.SIGINT, handleSigint)

def getLength(urls: list):
    async def contentLength(url):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                return response.content_length

    loop = asyncio.get_event_loop()
    tasks = [contentLength(url) for url in urls]
    totalContentLength = loop.run_until_complete(asyncio.gather(*tasks))

    return sum(totalContentLength)

def download(url, dir, file, log):
    logger.info(log)
    if not isinstance(url, list): url = [url]
    destPath = os.path.join(dir, file)

    print()

    progress = Progress(
        TextColumn("        "),
        TextColumn("[bold blue]Downloading"), BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        "eta", TimeRemainingColumn()
    )

    def __getUrl(taskId: TaskID, urls: list, path: str) -> None:
        progress.update(
            taskId,
            total=getLength(
                urls
            )
        )

        with open(path, "wb") as d:
            progress.start_task(taskId)

            for url in urls:
                response = urlopen(url)
                for data in iter(partial(response.read, 32768), b""):
                    d.write(data)
                    progress.update(taskId, advance=len(data))

                    if doneEvent.is_set():
                        return
    
    with progress:
        taskId = progress.add_task(
            "",
            filename=file,
            start=False
        )
        __getUrl(
            taskId,
            url,
            destPath
        )

    print()