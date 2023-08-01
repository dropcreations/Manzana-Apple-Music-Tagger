import os
import sys

from argparse import Namespace

from api import AppleMusic
from core import getFiles
from core import animartwork
from core import tag
from core import muxhls
from core import download
from utils import logger

def __getPath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(
            sys.executable
        )
    else:
        return os.path.dirname(
            os.path.abspath(
                __file__
            )
        )

def arguments(args: Namespace):
    CACHE = os.path.join(
        __getPath(),
        "cache"
    )

    if args.url == "reset":
        if os.path.exists(
            os.path.join(
                CACHE,
                "config.bin"
            )
        ):
            os.remove(
                os.path.join(
                    CACHE,
                    "config.bin"
                )
            )
    else:
        contents = getFiles(args.input)
        if os.path.isfile(args.input):
            os.chdir(
                os.path.abspath(
                    os.path.dirname(
                        args.input
                    )
                )
            )
        else:
            os.chdir(
                os.path.abspath(
                    args.input
                )
            )

        applemusic = AppleMusic(
            CACHE,
            args.sync,
            args.skip_video
        )

        data = applemusic.getInfo(args.url)

        if not args.no_cover:
            if "coverUrl" in data:
                if os.path.exists("Cover.jpg"):
                    os.remove("Cover.jpg")

                download(
                    data["coverUrl"],
                    os.getcwd(),
                    "Cover.jpg",
                    "Downloading album artwork..."
                )

        if args.animartwork:
            if "animartwork" in data:
                anim = animartwork(data["animartwork"])

                if anim:
                    if os.path.exists("Cover.mp4"):
                        os.remove("Cover.mp4")

                    download(
                        anim[0],
                        os.getcwd(),
                        "Cover.mp4",
                        f"Getting {anim[1]} animated artwork..."
                    )

                    if os.path.exists("Cover.mp4"):
                        logger.info("Muxing animated artwork...")
                        
                        if muxhls("Cover.mp4", "_Cover.mp4") == 0:
                            os.remove("Cover.mp4")
                            os.rename("_Cover.mp4", "Cover.mp4")
                        else:
                            if os.path.exists("_Cover.mp4"):
                                os.remove("_Cover.mp4")
            else:
                logger.warning("No animated artworks available!")

        try:
            for i, file in enumerate(contents):
                tag(
                    file,
                    data["streams"][i],
                    nocover=args.no_cover,
                    nolrc=args.no_lrc,
                    mediaUserToken=applemusic.isMediaUserToken
                )
        except IndexError:
            pass

        logger.info("Done.")