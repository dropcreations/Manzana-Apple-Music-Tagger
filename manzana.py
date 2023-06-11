import os
import sys
import argparse

from rich.console import Console
from rich.traceback import install

from api import AppleMusic
from utils import Config
from utils import Logger
from utils import Cache
from handler import getFiles, getAnimated
from handler import download, muxhls
from handler import tag

def getPath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

CACHE = os.path.join(getPath(), "cache")
CONFIG = os.path.join(getPath(), "config.json")

install()
Cache(CACHE)

logger = Logger("Manzana")
console = Console()
config = Config(configJson=CONFIG, cache=CACHE)

LOGO = r"""


        [bright_white bold]$$$$$$\$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$$\ $$$$$$\  $$$$$$$\   $$$$$$\  
        $$  _$$  _$$\  \____$$\ $$  __$$\ \____$$  |\____$$\ $$  __$$\  \____$$\ 
        $$ / $$ / $$ | $$$$$$$ |$$ |  $$ |  $$$$ _/ $$$$$$$ |$$ |  $$ | $$$$$$$ |
        $$ | $$ | $$ |$$  __$$ |$$ |  $$ | $$  _/  $$  __$$ |$$ |  $$ |$$  __$$ |
        $$ | $$ | $$ |\$$$$$$$ |$$ |  $$ |$$$$$$$$\\$$$$$$$ |$$ |  $$ |\$$$$$$$ |
        \__| \__| \__| \_______|\__|  \__|\________|\_______|\__|  \__| \_______|

                            ──── Apple Music Tagger ────[/]


"""

def main():
    parser = argparse.ArgumentParser(
        description="Manzana: Apple Music Tagger"
    )
    parser.add_argument(
        '-sc',
        '--sync',
        choices=["2", "3"],
        default="3",
        help="Timecode's ms point count in synced lyrics"
    )
    parser.add_argument(
        '-an',
        '--animated',
        help="Download the animated artwork if available",
        action="store_true"
    )
    parser.add_argument(
        '--no-cover',
        help="Don't save album artwork",
        action="store_true"
    )
    parser.add_argument(
        '--no-lrc',
        help="Don't save time-synced lyrics as a .lrc file",
        action="store_true"
    )
    parser.add_argument(
        '-p',
        '--path',
        help="Folder or file path for m4a/mp4 media",
        default=os.getcwd(),
    )
    parser.add_argument(
        'url',
        help="Apple Music URL",
        type=str
    )
    args = parser.parse_args()
    
    if args.url == "init": config.init()
    elif args.url == "reset": config.reset()
    else:
        applemusic = AppleMusic(CACHE,
                                args.animated,
                                int(args.sync),
                                config.mediaUserToken())
        
        data = applemusic.getInfo(args.url)
        contents = getFiles(args.path)

        if os.path.isfile(args.path): os.chdir(os.path.abspath(os.path.dirname(args.path)))
        else: os.chdir(os.path.abspath(args.path))

        if not args.no_cover:
            if "coverUrl" in data:
                if os.path.exists("Cover.jpg"): os.remove("Cover.jpg")
                download(data.get("coverUrl"),
                         os.getcwd(),
                         "Cover.jpg",
                         "Getting album artwork..."
                    )

        if args.animated:
            anim = getAnimated(data)
            if anim:
                if os.path.exists("Cover.mp4"): os.remove("Cover.mp4")
                download(anim[0],
                         os.getcwd(),
                         "Cover.mp4",
                         "Getting animated artwork..."
                    )
                if os.path.exists("Cover.mp4"):
                    if muxhls("Cover.mp4") == 0:
                        os.remove("Cover.mp4")
                        os.rename("_Cover.mp4", "Cover.mp4")
                    else:
                        if os.path.exists("_Cover.mp4"): os.remove("_Cover.mp4")

        try:
            for i, file in enumerate(contents):
                tag(file,
                    data["tracks"][i],
                    nocover=args.no_cover,
                    nolrc=args.no_lrc,
                    mediaUserToken=applemusic.isMediaUserToken
                )
        except IndexError: pass

        logger.info("Completed.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(LOGO)
    main()