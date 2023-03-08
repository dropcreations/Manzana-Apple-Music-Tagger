import os
import re
import json
import m3u8
import datetime
import requests
import xmltodict
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

class AppleMusic(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'content-type': 'application/json;charset=utf-8',
            'connection': 'keep-alive',
            'origin': 'https://music.apple.com',
            'referer': 'https://music.apple.com/',
            'accept-encoding': 'gzip, deflate',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        self.__load_cache()
        self.__load_settings()
        self.__get_access_token()
        self.__media_user_token()

    def __check_url(self, url):
        try:
            urlopen(url)
            return True
        except (URLError, HTTPError):
            return False

    def __process_url(self, url):
        __url = url.split('/')
        __id = __url[-1]
        __kind = __url[4]
        __storefront = __url[3]

        if __kind == "album":
            if len(__id.split('?i=')) > 1:
                __id = __id.split('?i=')[1]
                __kind = "song"

        if self.storefront is None: self.storefront = __storefront
        self.kind = __kind
        self.id = __id
        
    def __get_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "https://" + url # Add a default scheme if none is present
        if urlparse(url).netloc == "music.apple.com":
            if self.__check_url(url):
                self.__process_url(url)
            else: raise Exception("URL is invalid!")
        else: raise Exception("URL is invalid!")

    def __check_access_token(self, access_token):
        self.session.headers.update({
            'authorization': f'Bearer {access_token}'
        })
        response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")
        if response.status_code != 200:
            response = requests.get('https://music.apple.com/us/browse')
            if response.status_code != 200: raise Exception(response.text)

            index_js = re.search('(?<=index\.)(.*?)(?=\.js")', response.text).group(1)
            response = requests.get(f'https://music.apple.com/assets/index.{index_js}.js')
            if response.status_code != 200: raise Exception(response.text)

            access_token = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            
            self.__del_cache("access_token")
            self.__save_cache("access_token", access_token)

            return access_token
        else:
            return access_token
        
    def __get_access_token(self):
        access_token = self.__get_cache("access_token")

        if access_token is None:
            response = requests.get('https://music.apple.com/us/browse')
            if response.status_code != 200: raise Exception(response.text)

            index_js = re.search('(?<=index\.)(.*?)(?=\.js")', response.text).group(1)
            response = requests.get(f'https://music.apple.com/assets/index.{index_js}.js')
            if response.status_code != 200: raise Exception(response.text)

            access_token = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            self.__save_cache("access_token", access_token)

        access_token = self.__check_access_token(access_token)
        self.session.headers.update({
            'authorization': f'Bearer {access_token}'
        })

    def __media_user_token(self):
        with open(self.settings_file, "r") as s:
            settings = json.load(s)
        
        media_user_token = settings.get("media-user-token")

        if media_user_token != "":
            self.session.headers.update({
                "media-user-token": f"{media_user_token}"
            })

            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")
            response = json.loads(response.text)
            user_storefront = response["data"][0].get("id")
            user_language = response["data"][0]["attributes"].get("defaultLanguageTag")

            self.storefront = user_storefront
            self.language = user_language
            self.mut = "mut"
        else:
            self.storefront = None
            self.language = None
            self.mut = "no-mut"

    def __get_language(self):
        if self.language is None:
            response = self.session.get("https://amp-api.music.apple.com/v1/storefronts")
            storefronts_data = json.loads(response.text)

            for tag in storefronts_data["data"]:
                if tag["id"] == self.storefront:
                    self.language = tag["attributes"].get("defaultLanguageTag")
                    break

        self.session.headers.update({
            'accept-language': f'{self.language},en;q=0.9'
        })

    def __load_settings(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

        template = {
            "media-user-token": "",
        }

        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as s:
                json.dump(template, s, indent=4)

    def __load_cache(self):
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        self.cache_file = os.path.join(self.cache_dir, "cache.json")

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            open(self.cache_file, 'x')
        else:
            if not os.path.exists(self.cache_file):
                open(self.cache_file, 'x')

    def __save_cache(self, cache_key, cache_value):
        cache = {}
        if os.path.getsize(self.cache_file) > 0:
            with open(self.cache_file, 'r') as c:
                cache = json.load(c)

        cache[cache_key] = cache_value

        with open(self.cache_file, 'w') as c:
            json.dump(cache, c, indent=4)

    def __del_cache(self, cache_key):
        cache = {}
        if os.path.getsize(self.cache_file) > 0:
            with open(self.cache_file, 'r') as c:
                cache = json.load(c)
            del cache[cache_key]
            with open(self.cache_file, 'w') as c:
                json.dump(cache, c, indent=4)

    def __get_cache(self, cache_key):
        cache = {}
        if os.path.getsize(self.cache_file) > 0:
            with open(self.cache_file, 'r') as c:
                cache = json.load(c)
            if cache_key in cache:
                return cache[cache_key]

    def __get_json(self):
        cache_key = f"{self.storefront}:{self.id}:{self.kind}:{self.mut}"
        cached_response = self.__get_cache(cache_key)
        if cached_response is not None:
            return json.loads(cached_response)
        
        self.__get_access_token()
        self.__get_language()

        api_url = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'

        if self.kind == "album" or self.kind == "song":
            params = {
                'art[url]': 'f',
                'extend': 'editorialArtwork,editorialVideo,extendedAssetUrls',
                'fields[artists]': 'name,url',
                'fields[record-labels]': 'name,url',
                'format[resources]': 'map',
                'include': 'record-labels,artists',
                'include[music-videos]': 'artists',
                'include[songs]': 'artists,composers,albums,lyrics',
                'l': f'{self.language}'
            }

        elif self.kind == "artist":
            params = {
                'art[url]': 'c,f',
                'extend': 'editorialArtwork,editorialVideo,extendedAssetUrls,artistBio,bornOrFormed,hero,isGroup,origin,plainEditorialNotes',
                'extend[playlists]': 'trackCount',
                'format[resources]': 'map',
                'include': 'record-labels,artists',
                'include[music-videos]': 'artists',
                'include[songs]': 'artists,albums',
                'limit[artists:top-songs]': '20',
                'l': f'{self.language}',
                'views': 'appears-on-albums,compilation-albums,featured-albums,featured-on-albums,featured-release,full-albums,latest-release,live-albums,more-to-hear,more-to-see,playlists,radio-shows,similar-artists,singles,top-music-videos,top-songs'
            }

        elif self.kind == "playlist":
            params = {
                'art[url]': 'f',
                'extend': 'editorialArtwork,editorialVideo,trackCount',
                'fields[albums]': 'name,artwork,playParams,url',
                'fields[apple-curators]': 'name,url',
                'fields[artists]': 'name,artwork,url',
                'fields[curators]': 'name,url',
                'fields[songs]': 'name,artistName,curatorName,composerName,artwork,playParams,contentRating,albumName,url,durationInMillis,audioTraits,extendedAssetUrls',
                'format[resources]': 'map',
                'include': 'tracks,curator',
                'include[music-videos]': 'artists',
                'include[songs]': 'artists',
                'limit[tracks]': '300',
                'limit[view.contributors]': '15',
                'limit[view.featured-artists]': '15',
                'limit[view.more-by-curator]': '15',
                'omit[resource]': 'autos',
                'l': f'{self.language}',
                'views': 'contributors,featured-artists,more-by-curator'
            }

        elif self.kind == "music-video":
            params = {
                'art[url]': 'f',
                'fields[artists]': 'name,url',
                'format[resources]': 'map',
                'include[music-videos]': 'artists',
                'omit[resource]': 'autos',
                'l': f'{self.language}',
                'views': 'more-by-artist,more-in-genre'
            }

        self.session.params = params
        response = self.session.get(api_url)
        self.__save_cache(cache_key, response.text)
        return json.loads(response.text)
    
    def __remove_html_tags(self, quote):
        tags = re.compile('<.*?>')
        return re.sub(tags, '', quote)
    
    def __get_artwork(self, artwork_key, file_format="jpg"):
        url = artwork_key.get("url")
        width = artwork_key.get("width")
        height = artwork_key.get("height")

        url = url.replace("{w}", str(width))
        url = url.replace("{h}", str(height))
        url = url.replace("{f}", file_format)

        return url

    def __get_editorial_artwork(self, editorial_artwork_key):
        url = editorial_artwork_key["staticDetailSquare"].get("url")
        width = editorial_artwork_key["staticDetailSquare"].get("width")
        height = editorial_artwork_key["staticDetailSquare"].get("height")

        url = url.replace("{w}", str(width))
        url = url.replace("{h}", str(height))
        url = url.replace("{f}", "png")

        return url

    def __get_editorial_video(self, editorial_video_key, _type="square"):
        if _type == "square":
            m3u8_url = editorial_video_key["motionDetailSquare"].get("video")
            m3u8_data = m3u8.load(m3u8_url)
        elif _type == "tall":
            m3u8_url = editorial_video_key["motionDetailTall"].get("video")
            m3u8_data = m3u8.load(m3u8_url)

        m3u8_info = []
        m3u8_data = m3u8_data.data
        for i in range(len(m3u8_data["playlists"])):
            m3u8_dict = {
                "id": i,
                "uri": f'{m3u8_data["playlists"][i].get("uri")}',
                "resolution": f'{m3u8_data["playlists"][i]["stream_info"].get("resolution")}',
                "frame_rate": f'{m3u8_data["playlists"][i]["stream_info"].get("frame_rate")}',
                "codecs": f'{m3u8_data["playlists"][i]["stream_info"].get("codecs")}',
                "video_range": f'{m3u8_data["playlists"][i]["stream_info"].get("video_range")}',
                "average_bandwidth": f'{round((m3u8_data["playlists"][i]["stream_info"].get("average_bandwidth"))/1000000, 2)}'
            }
            m3u8_info.append(m3u8_dict)
        
        return m3u8_info
    
    def __get_lyrics(self, _ttml):
        ttml = xmltodict.parse(_ttml)

        lyricist_ = ttml["tt"]["head"]["metadata"]["iTunesMetadata"]["songwriters"].get("songwriter")
        if not isinstance(lyricist_, list):
            lyricist = lyricist_
        else:
            lyricist = ", ".join(lyricist_[0:-1])
            lyricist += f" & {lyricist_[-1]}"

        synced_lyrics = []
        normal_lyrics = []
        lyrics_info = {}

        song_part = ttml["tt"]["body"].get("div")

        if not isinstance(song_part, list):
            song_part = [song_part]
        for lines in song_part:
            if "p" in lines:
                p = lines.get("p")
                if not isinstance(p, list):
                    p = [p]
                for line in p:
                    begin_ts = line.get("@begin")
                    if begin_ts.endswith('s'): begin_ts = begin_ts[0:-1]

                    ts_format = begin_ts.split(':')
                    ts_format[-1] = format(float(ts_format[-1]), '.3f')
                    ts_format[-1] = str(ts_format[-1]).zfill(6)
                    
                    begin_ts = ":".join(ts_format)

                    if len(ts_format) > 2: begin_ts = begin_ts[-9:]
                    ts_parts = begin_ts.split(':')

                    if len(ts_parts) == 1:
                        begin_ts = str(datetime.timedelta(seconds=float(begin_ts)))
                        begin_ts = begin_ts[2:-3]
                    elif len(ts_parts) == 2:
                        if len(begin_ts) != 9:
                            if float(ts_parts[0]) < 10: begin_ts = f"0{begin_ts}"
                            elif float(ts_parts[0]) >= 10: begin_ts = begin_ts
                    
                    synced_line = f'[{begin_ts}] {line.get("#text")}'
                    synced_lyrics.append(synced_line)
                    normal_lyrics.append(line.get("#text"))

        lyrics_info["synced_lyrics"] = synced_lyrics
        lyrics_info["normal_lyrics"] = normal_lyrics
        lyrics_info["lyricist"] = lyricist

        return lyrics_info
    
    def __get_album(self):
        data = self.__get_json()
        id = data["data"][0].get("id")
        resources = data["resources"]["albums"][id]["attributes"]

        release_date = resources.get("releaseDate")
        upc = resources.get("upc")
        record_label = resources.get("recordLabel")
        track_count = resources.get("trackCount")
        is_compilation = resources.get("isCompilation")
        name = resources.get("name")
        album_artist = resources.get("artistName")

        copyright_info = None
        album_genre = None
        album_rating = None
        external_cover = None
        video_square = None
        video_tall = None
        standard_note = None
        short_note = None
        embed_cover = None
        track_genre = None
        track_rating = None
        lrc = None

        if "copyright" in resources:
            copyright_info = resources.get("copyright")

        if "genreNames" in resources:
            album_genre = resources.get("genreNames")

        if "contentRating" in resources:
            album_rating = resources.get("contentRating")

        if "editorialArtwork" in resources:
            if "staticDetailSquare" in resources["editorialArtwork"]:
                external_cover = self.__get_editorial_artwork(resources["editorialArtwork"])
            else:
                external_cover = self.__get_artwork(resources["artwork"], "png")

        if "editorialVideo" in resources:
            video_square = self.__get_editorial_video(resources["editorialVideo"], "square")
            video_tall = self.__get_editorial_video(resources["editorialVideo"], "tall")

        if "editorialNotes" in resources:
            if "standard" in resources["editorialNotes"]:
                standard_note = self.__remove_html_tags(resources["editorialNotes"].get("standard"))
            if "short" in resources["editorialNotes"]:
                short_note = self.__remove_html_tags(resources["editorialNotes"].get("short"))

        if "artwork" in resources:
            embed_cover = self.__get_artwork(resources["artwork"])

        track_ids = []
        track_data = []

        for track_id in data["resources"]["albums"][id]["relationships"]["tracks"]["data"]:
            track_ids.append(track_id.get("id"))

        for _id in track_ids:
            songs = data["resources"]["songs"][_id]["attributes"]
            track_no = songs.get("trackNumber")
            if "genreNames" in songs: track_genre = songs.get("genreNames")
            if "contentRating" in songs: track_rating = songs.get("contentRating")
            isrc = songs.get("isrc")
            composer = songs.get("composerName")
            disc_no = songs.get("discNumber")
            track_name = songs.get("name")
            artist = songs.get("artistName")
            
            if "lyrics" in data["resources"]:
                if songs.get("hasTimeSyncedLyrics"):
                    ttml = data["resources"]["lyrics"][_id]["attributes"].get("ttml")
                    lrc = self.__get_lyrics(ttml)

            track_info = {
                "name": track_name,
                "artist": artist,
                "composer": composer,
                "genre": track_genre if track_genre else None,
                "rating": track_rating if track_rating else None,
                "isrc": isrc,
                "disc_no": disc_no,
                "track_no": track_no,
                "lyricist": lrc["lyricist"] if lrc else None,
                "lyrics": lrc["normal_lyrics"] if lrc else None,
                "synced_lyrics": lrc["synced_lyrics"] if lrc else None
            }

            track_data.append(track_info)

        return {
            "name": name,
            "artist": album_artist,
            "release_date": release_date,
            "track_count": track_count,
            "upc": upc,
            "record_label": record_label,
            "compilation": is_compilation,
            "copyright": copyright_info if copyright_info else None,
            "genre": album_genre if album_genre else None,
            "rating": album_rating if album_rating else None,
            "external_cover": external_cover if external_cover else None,
            "video_square": video_square if video_square else None,
            "video_tall": video_tall if video_tall else None,
            "standard_note": standard_note if standard_note else None,
            "short_note": short_note if short_note else None,
            "embed_cover": embed_cover if embed_cover else None,
            "tracks": track_data
        }
    
    def __get_song(self):
        data = self.__get_json()
        id = data["data"][0].get("id")
        resources = data["resources"]["songs"][id]["attributes"]

        release_date = resources.get("releaseDate")
        name = resources.get("name")
        track_no = resources.get("trackNumber")
        isrc = resources.get("isrc")
        composer = resources.get("composerName")
        disc_no = resources.get("discNumber")
        artist = resources.get("artistName")

        copyright_info = None
        album_genre = None
        album_rating = None
        genre = None
        rating = None
        external_cover = None
        video_square = None
        video_tall = None
        standard_note = None
        short_note = None
        embed_cover = None
        lrc = None

        if "genreNames" in resources:
            genre = resources.get("genreNames")

        if "contentRating" in resources:
            rating = resources.get("contentRating")

        if "artwork" in resources:
            embed_cover = self.__get_artwork(resources["artwork"])

        album_id = data["resources"]["songs"][id]["relationships"]["albums"]["data"][0].get("id")
        album = data["resources"]["albums"][album_id].get("attributes")

        if "lyrics" in data["resources"]:
            lyrics_id = data["resources"]["songs"][id]["relationships"]["lyrics"]["data"][0].get("id")
            if resources.get("hasTimeSyncedLyrics"):
                ttml = data["resources"]["lyrics"][lyrics_id]["attributes"].get("ttml")
                lrc = self.__get_lyrics(ttml)

        if "copyright" in album:
            copyright_info = album.get("copyright")

        if "genreNames" in album:
            album_genre = album.get("genreNames")

        if "contentRating" in album:
            album_rating = album.get("contentRating")

        upc = album.get("upc")
        record_label = album.get("recordLabel")
        track_count = album.get("trackCount")
        is_compilation = album.get("isCompilation")
        album_name = album.get("name")
        album_artist = album.get("artistName")

        if "editorialVideo" in album:
            video_square = self.__get_editorial_video(album["editorialVideo"], "square")
            video_tall = self.__get_editorial_video(album["editorialVideo"], "tall")

        if "editorialArtwork" in album:
            if "staticDetailSquare" in album["editorialArtwork"]:
                external_cover = self.__get_editorial_artwork(album["editorialArtwork"])
            else:
                external_cover = self.__get_artwork(album["artwork"], "png")

        if "editorialNotes" in album:
            if "standard" in album["editorialNotes"]:
                standard_note = self.__remove_html_tags(album["editorialNotes"].get("standard"))
            if "short" in album["editorialNotes"]:
                short_note = self.__remove_html_tags(album["editorialNotes"].get("short"))

        track_data = []
        track_info = {
            "name": name,
            "artist": artist,
            "composer": composer,
            "genre": genre if genre else None,
            "rating": rating if rating else None,
            "isrc": isrc,
            "disc_no": disc_no,
            "track_no": track_no,
            "lyricist": lrc["lyricist"] if lrc else None,
            "lyrics": lrc["normal_lyrics"] if lrc else None,
            "synced_lyrics": lrc["synced_lyrics"] if lrc else None
        }
        track_data.append(track_info)

        return {
            "name": album_name,
            "artist": album_artist,
            "release_date": release_date,
            "track_count": track_count,
            "upc": upc,
            "record_label": record_label,
            "compilation": is_compilation,
            "copyright": copyright_info if copyright_info else None,
            "genre": album_genre if album_genre else None,
            "rating": album_rating if album_rating else None,
            "external_cover": external_cover if external_cover else None,
            "video_square": video_square if video_square else None,
            "video_tall": video_tall if video_tall else None,
            "standard_note": standard_note if standard_note else None,
            "short_note": short_note if short_note else None,
            "embed_cover": embed_cover if embed_cover else None,
            "tracks": track_data
        }

    def __get_playlist(self):
        data = self.__get_json()

    def __get_artist(self):
        data = self.__get_json()

    def __get_music_video(self):
        data = self.__get_json()
        id = data["data"][0].get("id")
        resources = data["resources"]["music-videos"][id]["attributes"]

        duration = resources.get("durationInMillis")
        duration = str(datetime.timedelta(milliseconds=duration))[3:-7]

        release_date = resources.get("releaseDate")
        name = resources.get("name")
        artist = resources.get("artistName")
        isrc = resources.get("isrc")

        genre = None
        rating = None
        embed_cover = None

        if "genreNames" in resources:
            genre = resources.get("genreNames")

        if "contentRating" in resources:
            rating = resources.get("contentRating")

        if "artwork" in resources:
            embed_cover = self.__get_artwork(resources["artwork"])

        return {
            "name": name,
            "artist": artist,
            "release_date": release_date,
            "isrc": isrc,
            "duration": duration,
            "genre": genre if genre else None,
            "rating": rating if rating else None,
            "embed_cover": embed_cover if embed_cover else None
        }

    def get_info(self, url):
        self.__get_url(url)

        if self.kind == "album": return self.__get_album()
        elif self.kind == "song": return self.__get_song()
        elif self.kind == "playlist": return self.__get_playlist()
        elif self.kind == "artist": return self.__get_artist()
        elif self.kind == "music-video": return self.__get_music_video()