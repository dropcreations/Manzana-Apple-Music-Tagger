import os
from urllib import request
from mutagen.flac import FLAC
from mutagen.flac import Picture
from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover
from sanitize_filename import sanitize
from prettytable.colortable import ColorTable, Theme

def get_info(info, i):
    global album_name; album_name = info.get("name")
    global album_artist; album_artist = info.get("artist")
    global release_date; release_date = info.get("release_date")
    global album_genre; album_genre = info.get("genre")
    global album_rating; album_rating = info.get("rating")
    global track_count; track_count = info.get("track_count")
    global upc; upc = info.get("upc")
    global record_label; record_label = info.get("record_label")
    global copyright_info; copyright_info = info.get("copyright")
    global track_name; track_name = info["tracks"][i].get("name")
    global track_artist; track_artist = info["tracks"][i].get("artist")
    global composer; composer = info["tracks"][i].get("composer")
    global track_genre; track_genre = info["tracks"][i].get("genre")
    global track_rating; track_rating = info["tracks"][i].get("rating")
    global embed_cover; embed_cover = info.get("embed_cover")
    global isrc; isrc = info["tracks"][i].get("isrc")
    global disc_no; disc_no = info["tracks"][i].get("disc_no")
    global track_no; track_no = info["tracks"][i].get("track_no")
    global lyricist; lyricist = info["tracks"][i].get("lyricist")
    global lyrics; lyrics = info["tracks"][i].get("lyrics")

def get_container(file_path):
    media_type = os.path.splitext(file_path)[1]
    if media_type == ".flac":
        return "flac"
    elif media_type == ".m4a":
        return "m4a"
    elif media_type == ".mp4":
        return "mp4"

def tag_audio(file_path, info, i):
    get_info(info, i)
    ext = get_container(file_path)

    if ext == "flac":
        tagger = FLAC(file_path)
        tagger.delete()
        tagger.clear_pictures()
        tagger['title'] = [track_name]
        tagger['album'] = [album_name]
        tagger['artist'] = [track_artist]
        tagger['albumartist'] = [album_artist]
        tagger['date'] = [release_date]
        tagger['composer'] = [composer]
        tagger['genre'] = album_genre if album_genre == track_genre else track_genre
        tagger['discnumber'] = [f'{disc_no}']
        tagger['totaldiscs'] = [f'{disc_no}']
        tagger['tracknumber'] = [f'{track_no}']
        tagger['totaltracks'] = [f'{track_count}']
        tagger['copyright'] = [copyright_info]
        tagger['isrc'] = [isrc]

        if album_rating:
            if track_rating:
                if album_rating == track_rating:
                    if album_rating == "explicit": tagger['rating'] = ['Explicit']
                    else: tagger['rating'] = ['Clean']
                else:
                    if track_rating == "explicit": tagger['rating'] = ['Explicit']
                    else: tagger['rating'] = ['Clean']

        if lyricist: tagger["Lyricist"] = [lyricist]
        if lyrics: tagger["lyrics"] = lyrics
        tagger['Label'] = [record_label]
        tagger['UPC'] = [upc]

        image = Picture()
        image.type = 3
        image.mime = 'image/jpeg'
        if not os.path.exists("Cover.jpg"):
            request.urlretrieve(embed_cover, f"Cover.jpg")
        with open("Cover.jpg", 'rb') as cover:
            image.data = cover.read()
        
        tagger.add_picture(image)
        tagger.pprint()
        tagger.save()

    elif ext == "m4a":
        tagger = MP4(file_path)
        tagger.delete()
        tagger['\xa9nam'] = [track_name]
        tagger['\xa9alb'] = [album_name]
        tagger['\xa9ART'] = [track_artist]
        tagger['aART'] = [album_artist]
        tagger['\xa9day'] = [release_date]
        tagger['\xa9wrt'] = [composer]
        tagger['\xa9gen'] = album_genre if album_genre == track_genre else track_genre
        tagger['disk'] = [(int(disc_no), int(disc_no))]
        tagger['trkn'] = [(int(track_no), int(track_count))]
        tagger['cprt'] = [copyright_info]
        tagger['----:com.apple.itunes:ISRC'] = [isrc.encode()]
        tagger['----:com.apple.itunes:Label'] = [record_label.encode()]
        tagger['----:com.apple.itunes:UPC'] = [upc.encode()]

        if album_rating:
            if track_rating:
                if album_rating == track_rating:
                    if album_rating == "explicit": tagger['rtng'] = [4]
                    else: tagger['rtng'] = [2]
                else:
                    if track_rating == "explicit": tagger['rtng'] = [4]
                    else: tagger['rtng'] = [2]
        
        tagger['stik'] = [1]
        if lyrics: tagger['\xa9lyr'] = lyrics
        if lyricist: tagger['----:com.apple.itunes:Lyricist'] = [lyricist.encode()]

        if not os.path.exists("Cover.jpg"):
            request.urlretrieve(embed_cover, f"Cover.jpg")
        image = open("Cover.jpg", 'rb').read()
        tagger['covr'] = [MP4Cover(image, MP4Cover.FORMAT_JPEG)]

        tagger.save()
    
    trackno = str(info["tracks"][i].get("track_no")).zfill(2)
    trackname = info["tracks"][i].get("name")

    return sanitize(f"{trackno} - {trackname}.{ext}")

def viewTracks(info):
    table = ColorTable(theme=Theme(default_color='90'))
    table.field_names = [" No ", "Name"]
    table.align["No"] = "c"
    table.align["Name"] = "l"

    for i in range(len(info.get("tracks"))):
        no = info["tracks"][i].get("track_no")
        no = str(no).zfill(2)
        t_name = info["tracks"][i].get("name")
        table.add_row([no, t_name])

    table = str(table)
    table = table.replace("\n", "\n\t")
    print(f'\t{table}')

def viewInfo(info, i):
    get_info(info, i)

    table = ColorTable(theme=Theme(default_color='90'))
    table.field_names = ["Name", "Value"]
    table.align["Name"] = "l"
    table.align["Value"] = "l"

    table.add_row(["Title", track_name])
    table.add_row(["Album", album_name])
    table.add_row(["Artist", track_artist])
    table.add_row(["Album artist", album_artist])
    table.add_row(["Release date", release_date])
    if track_genre: table.add_row(["Genre", ", ".join(track_genre)])
    table.add_row(["Composer", composer])
    table.add_row(["Disc no.", disc_no])
    table.add_row(["Track no.", track_no])
    table.add_row(["Track count", track_count])
    if copyright_info: table.add_row(["Copyright", copyright_info])
    table.add_row(["ISRC", isrc])
    table.add_row(["UPC", upc])
    table.add_row(["Record label", record_label])
    if track_rating: table.add_row(["Content rating", track_rating])

    table = str(table)
    table = table.replace("\n", "\n\t")
    print(f'\t{table}')