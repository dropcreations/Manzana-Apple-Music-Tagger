import os
import signal
import subprocess

from threading import Event
from functools import partial
from urllib.request import urlopen

from utils import Logger

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
logger = Logger("Handler")

def handleSigint(signum, frame):
    doneEvent.set()

signal.signal(signal.SIGINT, handleSigint)

def download(url, dir, file, log):
    logger.info(log)
    print()
    destPath = os.path.join(dir, file)

    progress = Progress(
        TextColumn("        "),
        TextColumn("[bold blue]Downloading"), BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        "eta", TimeRemainingColumn()
    )

    def __getUrl(taskId: TaskID, url: str, path: str) -> None:
        response = urlopen(url)
        progress.update(taskId, total=int(response.info()["Content-length"]))

        with open(path, "wb") as d:
            progress.start_task(taskId)

            for data in iter(partial(response.read, 32768), b""):
                d.write(data)
                progress.update(taskId, advance=len(data))

                if doneEvent.is_set():
                    return
    
    with progress:
        taskId = progress.add_task("download",
                                   filename=file,
                                   start=False)
        __getUrl(taskId, url, destPath)
    print()

def muxhls(input):
    try:
        retCode = subprocess.Popen(["mp4box", "-add", input,
                                    "-new", f"_{input}"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT).wait()
    except Exception:
        retCode = 1
    return retCode