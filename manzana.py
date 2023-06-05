import os
import argparse
from tagger import tag
from utils import Logger
from handler import getFiles
from handler import getAnimated
from handler import getOriginal
from applemusic import AppleMusic
from rich.traceback import install
from urllib.request import urlretrieve

install()
logger = Logger("Manzana")

LOGO = r"""


            $$$$$$\$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$$\ $$$$$$\  $$$$$$$\   $$$$$$\  
            $$  _$$  _$$\  \____$$\ $$  __$$\ \____$$  |\____$$\ $$  __$$\  \____$$\ 
            $$ / $$ / $$ | $$$$$$$ |$$ |  $$ |  $$$$ _/ $$$$$$$ |$$ |  $$ | $$$$$$$ |
            $$ | $$ | $$ |$$  __$$ |$$ |  $$ | $$  _/  $$  __$$ |$$ |  $$ |$$  __$$ |
            $$ | $$ | $$ |\$$$$$$$ |$$ |  $$ |$$$$$$$$\\$$$$$$$ |$$ |  $$ |\$$$$$$$ |
            \__| \__| \__| \_______|\__|  \__|\________|\_______|\__|  \__| \_______|

                                   ──── Apple Music Tagger ────


"""

def main():
    parser = argparse.ArgumentParser(
        description="Manzana: Apple Music Downloader"
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
        '-oc',
        '--original',
        help="Save original artwork as external cover",
        action="store_true"
    )
    parser.add_argument(
        '-cn',
        '--no-cache',
        help="Don't look for cache",
        action="store_true"
    )
    parser.add_argument(
        '-ln',
        '--no-lrc',
        help="Don't save synced lyrics as a .lrc file",
        action="store_true"
    )
    parser.add_argument(
        '-p',
        '--path',
        help="Folder or file path for media",
        default="current",
    )
    parser.add_argument(
        'url',
        help="Apple Music URL",
        type=str
    )
    args = parser.parse_args()

    applemusic = AppleMusic(syncPoints=int(args.sync),
                            anCover=args.animated,
                            noCache=args.no_cache)
    
    if args.url != "init":
        data = applemusic.getInfo(args.url)
        contents = getFiles(args.path)

        if "coverUrl" in data:
            if os.path.exists("Cover.jpg"): os.remove("Cover.jpg")
            urlretrieve(data.get("coverUrl"), "Cover.jpg")

        if args.animated: getAnimated(data)

        for i, file in enumerate(contents):
            tag(file, data["tracks"][i], noLrc=args.no_lrc, mediaUserToken=applemusic.mediaUserToken)

        if args.original:
            ori = getOriginal(data.get("coverUrl"))
            if ori:
                logger.info("Saving original artwork...")
                if os.path.exists("Cover.jpg"): os.remove("Cover.jpg")
                urlretrieve(ori[0], ori[1])

        logger.info("Completed.")
    else: logger.info("Get started!")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)
    main()