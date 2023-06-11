def musicVideo(data):
    info = {}
    attr = data["data"][0]["attributes"]
    
    __info = {}

    if "genreNames" in attr: __info["genre"] = ', '.join(attr.get("genreNames"))
    if "releaseDate" in attr: __info["releasedate"] = attr.get("releaseDate")
    if "isrc" in attr: __info["isrc"] = attr.get("isrc")
    if "name" in attr: __info["track"] = attr.get("name")
    if "artistName" in attr: __info["trackartist"] = attr.get("artistName")
    if "contentRating" in attr: __info["rating"] = attr.get("contentRating")

    __info["type"] = 6

    info["tracks"] = [__info]
    return info