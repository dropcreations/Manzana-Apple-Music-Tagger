import os
import argparse

from rich.console import Console
from rich.traceback import install

from control import arguments

install()

console = Console()

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
        '-v',
        '--version',
        version="Manzana: Apple Music Tagger v2.0.0",
        action="version"
    )
    parser.add_argument(
        '-sc',
        '--sync',
        choices=["2", "3"],
        default="2",
        help="Timecode's ms point count in synced lyrics. (default: 2)"
    )
    parser.add_argument(
        '-an',
        '--animartwork',
        help="Download the animated artwork if available. (default: False)",
        action="store_true"
    )
    parser.add_argument(
        '-cn',
        '--no-cover',
        help="Don't save album artwork. (default: False)",
        action="store_true"
    )
    parser.add_argument(
        '-ln',
        '--no-lrc',
        help="Don't save time-synced lyrics as a .lrc file. (default: False)",
        action="store_true"
    )
    parser.add_argument(
        '-sv',
        '--skip-video',
        help="Skip videos in an album. (default: False)",
        action="store_true"
    )
    parser.add_argument(
        '-i',
        '--input',
        help="Folder or file path for m4a/mp4 media files. (default: Current working directory)",
        default=os.getcwd(),
    )
    parser.add_argument(
        'url',
        help="Apple Music URL",
        type=str
    )
    args = parser.parse_args()
    arguments(args)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(LOGO)
    main()