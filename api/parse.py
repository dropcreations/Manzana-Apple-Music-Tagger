import m3u8
from api.lyrics import parseLyrics

def opt(d: dict):
    nd = {}

    for k, v in d.items():
        if v: nd[k] = v

    return nd

def parseJson(data, sync: int, skipVideo=False):
    media = {}
    mediaList = []

    for item in data:
        if item["type"] == "songs":
            song = {}
            attr = item["attributes"]

            song["type"] = 1
            song["album"] = attr["albumName"]
            song["genre"] = attr["genreNames"]
            song["trackno"] = attr["trackNumber"]
            song["releasedate"] = attr["releaseDate"]
            song["isrc"] = attr["isrc"]
            song["composer"] = attr["composerName"]
            song["discno"] = attr["discNumber"]
            song["song"] = attr["name"]
            song["songartist"] = attr["artistName"]
            song["previewUrl"] = attr["previews"][0]["url"]
            song["rating"] = attr["contentRating"] if "contentRating" in attr else None

            rela = item["relationships"]

            if "credits" in rela:
                credits = rela["credits"]["data"]
                if credits:

                    roles = []
                    creds = {}

                    for catagory in credits:
                        for credit in catagory["relationships"]["credit-artists"]["data"]:
                            for role in credit["attributes"]["roleNames"]:
                                if not role in roles:
                                    roles.append(role)
                                    creds[role] = [credit["attributes"]["name"]]
                                else:
                                    roleArtist: list = creds[role]
                                    roleArtist.append(credit["attributes"]["name"])
                                    creds[role] = roleArtist

                    song["credits"] = creds

            if "lyrics" in rela:
                if rela["lyrics"]["data"]:
                    song.update(
                        parseLyrics(
                            rela["lyrics"]["data"][0]["attributes"]["ttml"],
                            sync
                        )
                    )

            media["coverUrl"] = attr["artwork"]["url"].format(
                w=attr["artwork"]["width"],
                h=attr["artwork"]["height"]
            )
            
            attr = rela["albums"]["data"][0]["attributes"]

            song["copyright"] = attr["copyright"] if "copyright" in attr else None
            song["upc"] = attr["upc"]
            song["recordlabel"] = attr["recordLabel"] if "recordLabel" in attr else None
            song["trackcount"] = attr["trackCount"]
            song["albumartist"] = attr["artistName"]

            if "editorialVideo" in attr:
                if "motionDetailSquare" in attr["editorialVideo"]:
                    __data = m3u8.load(
                        attr["editorialVideo"]["motionDetailSquare"]["video"]
                    ).data

                    streamList = []

                    for i, variants in enumerate(__data["playlists"]):
                        codec = variants["stream_info"]["codecs"]

                        if "avc" in codec: codec = "AVC"
                        elif "hvc" in codec: codec = "HEVC"

                        streamList.append(
                            {
                                "id": i,
                                "fps": variants["stream_info"]["frame_rate"],
                                "codec": codec,
                                "range": variants["stream_info"]["video_range"],
                                "bitrate": f'{round((variants["stream_info"]["average_bandwidth"])/1000000, 2)} Mb/s',
                                "resolution": variants["stream_info"]["resolution"],
                                "uri": variants["uri"]
                            }
                        )

                    media["animartwork"] = streamList

            mediaList.append(opt(song))

        elif item["type"] == "music-videos":
            if not skipVideo:
                musicVideo = {}
                attr = item["attributes"]

                musicVideo["type"] = 6
                musicVideo["album"] = attr["albumName"] if "albumName" in attr else None
                musicVideo["genre"] = attr["genreNames"]
                musicVideo["releasedate"] = attr["releaseDate"]
                musicVideo["isrc"] = attr["isrc"]
                musicVideo["song"] = attr["name"]
                musicVideo["songartist"] = attr["artistName"]
                musicVideo["rating"] = attr["contentRating"] if "contentRating" in attr else None

                mediaList.append(opt(musicVideo))

    media["streams"] = mediaList
    return media