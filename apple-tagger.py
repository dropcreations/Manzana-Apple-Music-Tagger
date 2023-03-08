import os
import sys
import colorama
import argparse
from urllib import request
from colorama import Fore
colorama.init(autoreset=True)
from tagger import tag_audio
from tagger import viewTracks
from tagger import viewInfo
from applemusic import AppleMusic
from sanitize_filename import sanitize

content_FLAC = []
content_M4A = []

logo = f"""


         █████╗ ██████╗ ██████╗ ██╗     ███████╗   ███╗   ███╗██╗   ██╗ ██████╗██╗ █████╗ 
        ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝   ████╗ ████║██║   ██║██╔════╝██║██╔══██╗
        ███████║██████╔╝██████╔╝██║     █████╗     ██╔████╔██║██║   ██║╚█████╗ ██║██║  ╚═╝
        ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝     ██║╚██╔╝██║██║   ██║ ╚═══██╗██║██║  ██╗
        ██║  ██║██║     ██║     ███████╗███████╗   ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║╚█████╔╝
        ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝   ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝ ╚════╝ 

                    {Fore.GREEN + "Media file (FLAC/M4A) tagger using Apple Music credits"}

"""

def processFolder(dir):
    if dir == "current_working_directory":
        content = os.listdir(os.getcwd())
    else:
        content = os.listdir(dir)
        os.chdir(dir)
    
    for file in content:
        if os.path.splitext(file)[1] == ".flac":
            file_name = str(os.path.basename(os.path.splitext(file)[0])).zfill(2)
            file_name += f".flac"
            os.rename(file, file_name)
            content_FLAC.append(file_name)
        elif os.path.splitext(file)[1] == ".m4a":
            file_name = str(os.path.basename(os.path.splitext(file)[0])).zfill(2)
            file_name += f".m4a"
            os.rename(file, file_name)
            content_M4A.append(file_name)

def main():
    parser = argparse.ArgumentParser(
        description="Tag FLAC/M4A media files using Apple Music's credit info"
    )
    parser.add_argument(
        '-d',
        '--dir',
        help="folder path where media files contains for whole album tagging",
        default=None,
        type=str
    )
    parser.add_argument(
        '-f',
        '--file',
        help="audio file path for single track tagging",
        default=None,
        type=str
    )
    parser.add_argument(
        'url',
        help="url from Apple Music for a album or a track",
        type=str
    )
    args = parser.parse_args()

    if args.file and args.dir:
        print(Fore.YELLOW + "You have used both --file and --dir parameters. You can use only one at once")
        parser.print_help()
        sys.exit()

    if not args.file and not args.dir:
        args.dir = "current_working_directory"
    
    mediaFile = args.file
    mediaFolder = args.dir
    mediaURL = args.url

    applemusic = AppleMusic()
    info = applemusic.get_info(mediaURL)
    
    if mediaFolder:
        viewTracks(info)
        print("\nProcessing folder...")
        processFolder(mediaFolder)

        if len(content_FLAC) > 0: content_file = content_FLAC
        elif len(content_M4A) > 0: content_file = content_M4A

        content_file = sorted(content_file)

        for i in range(len(content_file)):
            print("\nTagging...")
            print("  |")
            print(f"  |--File: {content_file[i]}")
            fname = tag_audio(content_file[i], info, i)
            print(f"  |--Re-naming file as ({Fore.YELLOW + fname + Fore.WHITE})...")
            os.rename(content_file[i], fname)

            synced_lyrics = info["tracks"][i].get("synced_lyrics")

            if synced_lyrics:
                synced_lrc = "\n".join(synced_lyrics)
                print("  |--Saving time-synced lyrics...")
                with open(sanitize(f"{os.path.splitext(fname)[0]}.lrc"), 'w', encoding='utf-8') as slrc:
                    slrc.write(synced_lrc)
            else: print("  |--No time-synced lyrics to save")
            
            print("  |--done.")
    
    elif mediaFile:
        viewInfo(info, 0)
        print("\nTagging...")
        print("  |")
        print(f"  |--File: {mediaFile}")
        fname = tag_audio(mediaFile, info, 0)
        print(f"  |--Re-naming file as ({Fore.YELLOW + fname + Fore.WHITE})...")
        os.rename(mediaFile, fname)

        synced_lyrics = info["tracks"][0].get("synced_lyrics")

        if synced_lyrics:
            synced_lrc = "\n".join(synced_lyrics)
            print("  |--Saving time-synced lyrics...")
            with open(sanitize(f"{os.path.splitext(fname)[0]}.lrc"), 'w', encoding='utf-8') as slrc:
                slrc.write(synced_lrc)
        else: print("  |--No time-synced lyrics to save")

        print("  |--done.")

    os.remove("Cover.jpg")
    print("\nSaving album artwork...")
    external_cover = info.get("external_cover")
    if not os.path.exists("Cover.png"): request.urlretrieve(external_cover, f'Cover.png')
    else: print("An album artwork is already exsists.")
    print("Successfully completed.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(logo)
    main()