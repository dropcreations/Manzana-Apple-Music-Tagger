import os
import re
import sys
import json
import m3u8
import requests
from loggings import Logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

logger = Logger("AppleMusic")

class AppleMusic(object):
    def __init__(self, syncPoints: int, noCache: bool):
        self.session = requests.Session()
        self.session.headers = {
            'content-type': 'application/json;charset=utf-8',
            'connection': 'keep-alive',
            'accept': 'application/json',
            'origin': 'https://music.apple.com',
            'referer': 'https://music.apple.com/',
            'accept-encoding': 'gzip, deflate, br',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }

        self.sync_points = syncPoints
        self.no_cache = noCache

        self.storefront = "us"
        self.language = "en-US"
        self.media_user_token = False

        self.__load_cache()
        self.__get_access_token()
        self.__load_cookies()

    def __check_url(self, url):
        try:
            urlopen(url)
            return True
        except (URLError, HTTPError):
            return False
        
    def __get_url(self, url):
        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            url = "https://" + url # Add a default scheme if none is present

        if parsed_url.netloc == "music.apple.com":
            if self.__check_url(url):
                splits = url.split('/')

                __id = splits[-1]
                __kind = splits[4]
                __storefront = splits[3]

                if __kind == "album":
                    if len(__id.split('?i=')) > 1:
                        __id = __id.split('?i=')[1]
                        __kind = "song"

                if self.storefront is None: self.storefront = __storefront
                self.kind = __kind
                self.id = __id
            else: logger.error("URL is invalid!", 1)
        else: logger.error("URL is invalid!", 1)

    def __load_cache(self):
        logger.info("Loading cache...")

        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "cache")
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
        if os.path.getsize(self.cache_file) > 0:
            with open(self.cache_file, 'r') as c:
                cache = json.load(c)
                if cache_key in cache: return cache[cache_key]

    def __check_access_token(self, access_token):
        logger.info("Checking access token found in cache...")

        self.session.headers.update({
            'authorization': f'Bearer {access_token}'
        })

        response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")
        if response.status_code != 200:
            logger.info("Access token found in cache is expired!")
            self.__del_cache("access_token")
            self.__get_access_token()
        else:
            return access_token
        
    def __get_access_token(self):
        access_token = self.__get_cache("access_token")

        if access_token is None:
            logger.info("Fetching access token from web...")
            response = requests.get('https://music.apple.com/us/browse')
            if response.status_code != 200: raise Exception(response.text)

            index_js = re.search('(?<=index\.)(.*?)(?=\.js")', response.text).group(1)
            response = requests.get(f'https://music.apple.com/assets/index.{index_js}.js')
            if response.status_code != 200: raise Exception(response.text)

            access_token = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            self.__save_cache("access_token", access_token)
        else:
            access_token = self.__check_access_token(access_token)
        
        self.session.headers.update({
            'authorization': f'Bearer {access_token}'
        })

    def __media_user_token(self, cookies):
        if "media-user-token" in cookies:
            logger.info("Fetching media-user-token...")

            self.session.headers.update({
                "media-user-token": cookies.get("media-user-token")
            })

            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")
            response = json.loads(response.text)
            user_storefront = response["data"][0].get("id")
            user_language = response["data"][0]["attributes"].get("defaultLanguageTag")

            self.storefront = user_storefront
            self.language = user_language
            self.media_user_token = True

            self.session.headers.update({
                'accept-language': f'{self.language},en;q=0.9'
            })

    def __get_cookies_txt(self, cookie_file):
        cookies = {}
        with open(cookie_file, 'r') as c:
            for line in c:
                if not re.match(r'^\#', line):
                    items = line.strip().split("\t")
                    if len(items) > 1: cookies[items[5]] = items[6]
        return cookies

    def __get_cookies_json(self, cookie_file):
        cookies = {}
        with open(cookie_file, 'r') as c:
            c_json = json.load(c)
            for item in c_json:
                cookies[item.get("name")] = item.get("value")
        return cookies

    def __load_cookies(self):
        self.cookies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "cookies")

        logger.info("Loading cookies...")
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
            logger.warning("Cookies not found! Ignoring user subscription...")
        else:
            cookie_files = os.listdir(self.cookies_dir)
            if len(cookie_files) != 0:
                for cookie_file in cookie_files:
                    cookie_file = os.path.join(self.cookies_dir, cookie_file)

                    if os.path.splitext(cookie_file)[1] == ".txt":
                        cookies = self.__get_cookies_txt(cookie_file)
                    elif os.path.splitext(cookie_file)[1] == ".json":
                        cookies = self.__get_cookies_json(cookie_file)

                self.__media_user_token(cookies)
            else:
                logger.warning("Cookies not found! Ignoring user subscription...")

    def __get_json(self):
        logger.info("Getting API response...")

        cache_key = f"{self.kind}:{self.id}:{self.storefront}"

        if not self.no_cache:
            cached_response = self.__get_cache(cache_key)
            if cached_response is not None:
                logger.info("Using the response found in cache...")
                return cached_response

        apiUrl = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'

        if self.kind == "album" or self.kind == "song":
            params = {
                'extend': 'editorialArtwork,editorialVideo,extendedAssetUrls',
                'fields[artists]': 'name,url',
                'fields[record-labels]': 'name,url',
                'include': 'record-labels,artists',
                'include[music-videos]': 'artists',
                'include[albums]': 'artists',
                'include[songs]': 'artists,composers,albums,lyrics',
                'l': f'{self.language}'
            }

        elif self.kind == "music-video":
            params = {
                'fields[artists]': 'name,url',
                'include[music-videos]': 'artists',
                'l': f'{self.language}',
            }

        self.session.params = params

        response = self.session.get(apiUrl)
        response = json.loads(response.text)

        if not self.no_cache:
            if self.media_user_token:
                if not "errors" in response:
                    self.__save_cache(cache_key, response)
        
        return response
    
    def __get_ts(self, ts):
        ts = ts.replace('s', '')
        secs = float(ts.split(':')[-1])

        if ":" in ts: mins = ts.split(':')[-2]
        else: mins = 0

        if self.sync_points == 3: return f'{mins:0>2}:{secs:06.3f}'
        elif self.sync_points == 2: return f'{mins:0>2}:{secs:05.2f}'
    
    def __get_lyrics(self, ttml):
        ttml = BeautifulSoup(ttml, "lxml")

        _songwriters = []
        _normalLyrics = []
        _syncedLyrics = []

        songwriters = ttml.find_all("songwriter")
        if len(songwriters) > 0:
            for songwriter in songwriters:
                _songwriters.append(songwriter.text)

        for line in ttml.find_all("p"):
            _normalLyrics.append(line.text)
            if "span" in str(line):
                span = BeautifulSoup(str(line), "lxml")
                for s in span.find_all("span", attrs={'begin': True, 'end': True}):
                    begin = self.__get_ts(s.get("begin"))
                    _syncedLyrics.append(f"[{begin}]{s.text}")
            else:
                begin = self.__get_ts(line.get("begin"))
                _syncedLyrics.append(f"[{begin}]{line.text}")

        return {
            "songwriters": _songwriters,
            "lyrics": _normalLyrics,
            "timeSyncedLyrics": _syncedLyrics
        }
    
    def __remove_tags(self, string: str): # remove html tags in editorial notes
        string = string.replace("\n", "")
        tags = re.compile('<.*?>')
        return re.sub(tags, '', string)
    
    def __check_artwork(self, url): # check if artwork url is vaild
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        response = requests.head(url)
        if response.headers["content-type"] in image_formats:
            return True
        return False
    
    def __get_artwork(self, key):
        url = key.get("url")

        if os.path.splitext(url)[1] != ".{f}":
            url = os.path.splitext(url)[0] + ".{f}"
        
        width = key.get("width")
        height = key.get("height")

        original = "https://a1.mzstatic.com/r40/" + "/".join(url.split("/")[5:-1])
        if not self.__check_artwork(original): original = None

        jpgUrl = url.format(w=str(width), h=str(height), f="jpg")
        pngUrl = url.format(w=str(width), h=str(height), f="png")

        return {
            "originalUrl": original,
            "compressedUrl": {
                "jpg": jpgUrl,
                "png": pngUrl
            }
        }

    def __get_editorial_artwork(self, key):
        if "staticDetailSquare" in key:
            url = key["staticDetailSquare"].get("url")

            if os.path.splitext(url)[1] != ".{f}":
                url = os.path.splitext(url)[0] + ".{f}"
            
            width = key["staticDetailSquare"].get("width")
            height = key["staticDetailSquare"].get("height")

            original = "https://a1.mzstatic.com/r40/" + "/".join(url.split("/")[5:-1])
            if not self.__check_artwork(original): original = None

            jpgUrl = url.format(w=str(width), h=str(height), f="jpg")
            pngUrl = url.format(w=str(width), h=str(height), f="png")

            return {
                "originalUrl": original,
                "compressedUrl": {
                    "jpg": jpgUrl,
                    "png": pngUrl
                }
            }
        else:
            return None

    def __get_editorial_video(self, key):
        if "motionDetailSquare" in key:
            data = m3u8.load(key["motionDetailSquare"].get("video")).data
        else: return None

        __data = []

        for i, variants in enumerate(data["playlists"]):
            codec = variants["stream_info"].get("codecs")

            if "avc" in codec: codec = "AVC"
            elif "hvc" in codec: codec = "HEVC"

            __data.append({
                "id": i,
                "fps": variants["stream_info"].get("frame_rate"),
                "codec": codec,
                "range": variants["stream_info"].get("video_range"),
                "bitrate": f'{round((variants["stream_info"].get("average_bandwidth"))/1000000, 2)} Mb/s',
                "resolution": variants["stream_info"].get("resolution"),
                "uri": variants.get("uri")
            })
        
        return __data
    
    def __get_artists(self, data):
        if not isinstance(data, list):
            data = [data]
        
        artists = []

        for artist in data:
            artists.append(artist["attributes"].get("name"))

        return artists
    
    def __get_errors(self, errors):
        if not isinstance(errors, list): errors = [errors]
        for error in errors:
            err_status = error.get("status")
            err_detail = error.get("detail")
            logger.error(f"{err_status} - {err_detail}", 1)
    
    def __get_album(self):
        data = self.__get_json()
        
        if not "errors" in data:
            logger.info("Fetching album info...")

            __data = {}
            __tracks_ = []

            attributes = data["data"][0].get("attributes")
            relationships = data["data"][0].get("relationships")

            if "editorialNotes" in attributes:
                notes = {}

                if "standard" in attributes["editorialNotes"]:
                    notes["standard"] = self.__remove_tags(attributes["editorialNotes"].get("standard"))
                
                if "short" in attributes["editorialNotes"]:
                    notes["short"] = self.__remove_tags(attributes["editorialNotes"].get("short"))

                __data["notes"] = notes

            if "editorialVideo" in attributes:
                __data["animatedCover"] = self.__get_editorial_video(attributes["editorialVideo"])

            if "artwork" in attributes:
                __data["embedCover"] = self.__get_artwork(attributes["artwork"])

            if "editorialArtwork" in attributes:
                __data["externalCover"] = self.__get_editorial_artwork(attributes["editorialArtwork"])

            for track in relationships["tracks"].get("data"):
                __tracks = {}
                
                __tracks["type"] = track.get("type")[0:-1]
                __tracks["albumName"] = attributes.get("name")
                __tracks["albumArtist"] = self.__get_artists(relationships["artists"].get("data"))
                __tracks["trackNumber"] = track["attributes"].get("trackNumber")
                __tracks["trackCount"] = attributes.get("trackCount")
                __tracks["trackName"] = track["attributes"].get("name")
                __tracks["trackArtist"] = self.__get_artists(track["relationships"]["artists"].get("data"))
                __tracks["discNumber"] = track["attributes"].get("discNumber")
                __tracks["isrc"] = track["attributes"].get("isrc")
                __tracks["upc"] = attributes.get("upc")
                __tracks["genre"] = track["attributes"].get("genreNames")

                if "contentRating" in track["attributes"]: __tracks["rating"] = track["attributes"].get("contentRating")
                if "releaseDate" in track["attributes"]: __tracks["releaseDate"] = track["attributes"].get("releaseDate")
                if "composerName" in track["attributes"]: __tracks["composer"] = track["attributes"].get("composerName")
                if "recordLabel" in attributes: __tracks["recordLabel"] = attributes.get("recordLabel")
                if "copyright" in attributes: __tracks["copyright"] = attributes.get("copyright")

                if "lyrics" in track["relationships"]:
                    if len(track["relationships"]["lyrics"].get("data")) > 0:
                        __tracks.update(self.__get_lyrics(track["relationships"]["lyrics"]["data"][0]["attributes"].get("ttml")))

                __tracks_.append(__tracks)

            __data["tracks"] = __tracks_
            return __data
        else:
            self.__get_errors(data.get("errors"))

    def __get_song(self):
        data = self.__get_json()

        if not "errors" in data:
            logger.info("Fetching song info...")

            __data = {}
            __tracks_ = []

            attributes = data["data"][0]["relationships"]["albums"]["data"][0].get("attributes")

            if "editorialNotes" in attributes:
                notes = {}

                if "standard" in attributes["editorialNotes"]:
                    notes["standard"] = self.__remove_tags(attributes["editorialNotes"].get("standard"))
                
                if "short" in attributes["editorialNotes"]:
                    notes["short"] = self.__remove_tags(attributes["editorialNotes"].get("short"))

                __data["notes"] = notes

            if "editorialVideo" in attributes:
                __data["animatedCover"] = self.__get_editorial_video(attributes["editorialVideo"])

            if "artwork" in attributes:
                __data["embedCover"] = self.__get_artwork(attributes["artwork"])

            if "editorialArtwork" in attributes:
                __data["externalCover"] = self.__get_editorial_artwork(attributes["editorialArtwork"])

            for track in data.get("data"):
                __tracks = {}

                __tracks["type"] = track.get("type")[0:-1]
                __tracks["albumName"] = attributes.get("name")
                __tracks["albumArtist"] = self.__get_artists(track["relationships"]["albums"]["data"][0]["relationships"]["artists"].get("data"))
                __tracks["trackNumber"] = track["attributes"].get("trackNumber")
                __tracks["trackCount"] = attributes.get("trackCount")
                __tracks["trackName"] = track["attributes"].get("name")
                __tracks["trackArtist"] = self.__get_artists(track["relationships"]["artists"].get("data"))
                __tracks["discNumber"] = track["attributes"].get("discNumber")
                __tracks["isrc"] = track["attributes"].get("isrc")
                __tracks["upc"] = attributes.get("upc")
                __tracks["genre"] = track["attributes"].get("genreNames")

                if "contentRating" in track["attributes"]: __tracks["rating"] = track["attributes"].get("contentRating")
                if "releaseDate" in track["attributes"]: __tracks["releaseDate"] = track["attributes"].get("releaseDate")
                if "composerName" in track["attributes"]: __tracks["composer"] = track["attributes"].get("composerName")
                if "recordLabel" in attributes: __tracks["recordLabel"] = attributes.get("recordLabel")
                if "copyright" in attributes: __tracks["copyright"] = attributes.get("copyright")

                if "lyrics" in track["relationships"]:
                    if len(track["relationships"]["lyrics"].get("data")) > 0:
                        __tracks.update(self.__get_lyrics(track["relationships"]["lyrics"]["data"][0]["attributes"].get("ttml")))

                __tracks_.append(__tracks)

            __data["tracks"] = __tracks_
            return __data
        else: self.__get_errors(data.get("errors"))

    def __get_music_video(self):
        data = self.__get_json()

        if not "errors" in data:
            logger.info("Fetching music-video info...")

            __data = {}
            __track = {}

            attributes = data["data"][0].get("attributes")
            relationships = data["data"][0].get("relationships")

            __track["trackName"] = attributes.get("name")
            __track["trackArtist"] = self.__get_artists(relationships["artists"].get("data"))
            __track["isrc"] = attributes.get("isrc")
            if "genreNames" in attributes: __track["genre"] = attributes.get("genreNames")
            if "contentRating" in attributes: __track["rating"] = attributes.get("contentRating")
            __track["releaseDate"] = attributes.get("releaseDate")

            __data["tracks"] = [__track]

            return __data
        else: self.__get_errors(data.get("errors"))
    
    def get_info(self, url):
        self.__get_url(url)

        if self.kind == "album": return self.__get_album()
        elif self.kind == "song": return self.__get_song()
        elif self.kind == "music-video": return self.__get_music_video()