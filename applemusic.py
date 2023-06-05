import os
import re
import sys
import json
import m3u8
import requests
from utils import Cache
from utils import Logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
from rich.traceback import install
from urllib.error import URLError, HTTPError

install()

def __getPath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
CACHE = os.path.join(__getPath(), "cache")
if not os.path.exists(CACHE): os.makedirs(CACHE)

COOKIES = os.path.join(__getPath(), "cookies")
if not os.path.exists(COOKIES): os.makedirs(COOKIES)

cache = Cache(CACHE)
logger = Logger("AppleMusic")

class AppleMusic(object):
    def __init__(self, syncPoints: int, anCover: bool, noCache: bool):
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

        self.syncPoints = syncPoints
        self.noCache = noCache
        self.anCover = anCover

        self.storefront = "us"
        self.language = "en-US"
        self.mediaUserToken = self.__getCache()

        self.__accessToken()
        self.__mediaUserToken()

    def __getCache(self):
        cookies = {}
        cookie_files = os.listdir(COOKIES)

        if len(cookie_files) != 0:
            logger.info("Loading cookies...")
            for cookie_file in cookie_files:
                cookie_file = os.path.join(COOKIES, cookie_file)
                if os.path.splitext(cookie_file)[1] == ".txt":
                    with open(cookie_file, 'r') as c:
                        for line in c:
                            if not re.match(r'^\#', line):
                                items = line.strip().split("\t")
                                if len(items) > 1:
                                    cookies[items[5]] = items[6]
                elif os.path.splitext(cookie_file)[1] == ".json":
                    with open(cookie_file, 'r') as c:
                        c_json = json.load(c)
                        for item in c_json:
                            cookies[item.get("name")] = item.get("value")

            if "media-user-token" in cookies: return cookies.get("media-user-token")
            else: logger.warning("Unable to find media-user-token...Ignoring user subscription...")
        else: logger.info("Paste cookies file into ./cookies to use subscription...")

        return None

    def __checkUrl(self, url):
        try:
            urlopen(url)
            return True
        except (URLError, HTTPError):
            return False
        
    def __getUrl(self, url):
        parsedUrl = urlparse(url)
        if not parsedUrl.scheme: url = f"https://{url}"
        if parsedUrl.netloc == "music.apple.com":
            if self.__checkUrl(url):
                splits = url.split('/')

                id = splits[-1]
                kind = splits[4]

                if kind == "album":
                    if len(id.split('?i=')) > 1:
                        id = id.split('?i=')[1]
                        kind = "song"

                self.kind = kind
                self.id = id

            else: logger.error("URL is invalid!", 1)
        else: logger.error("URL is invalid!", 1)
        
    def __accessToken(self):
        accessToken = None

        if not self.noCache:
            accessToken = cache.get("access_token")

        if not accessToken:
            logger.info("Fetching access token from web...")
            response = requests.get('https://music.apple.com/us/browse')
            if response.status_code != 200: raise Exception(response.text)

            indexJs = re.search('(?<=index)(.*?)(?=\.js")', response.text).group(1)
            response = requests.get(f'https://music.apple.com/assets/index{indexJs}.js')
            if response.status_code != 200: raise Exception(response.text)

            accessToken = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            cache.set("access_token", accessToken)
        else:
            logger.info("Checking access token found in cache...")
            self.session.headers.update({'authorization': f'Bearer {accessToken}'})
            response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")

            if response.status_code != 200:
                logger.info("Access token found in cache is expired!")
                cache.delete("access_token")
                self.__accessToken()
        
        self.session.headers.update({
            'authorization': f'Bearer {accessToken}'
        })

    def __mediaUserToken(self):
        if self.mediaUserToken:
            logger.info("Fetching media-user-token...")
            self.session.headers.update({"media-user-token": self.mediaUserToken})
            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")
            if response.status_code == 200:
                response = json.loads(response.text)

                user_storefront = response["data"][0].get("id")
                user_language = response["data"][0]["attributes"].get("defaultLanguageTag")

                self.storefront = user_storefront
                self.language = user_language

                self.session.headers.update({'accept-language': f'{self.language},en;q=0.9'})

            else: logger.error("Invalid media-user-token found in cookies! Ignoring user subscription...")

    def __getErrors(self, errors):
        if not isinstance(errors, list):
            errors = [errors]
        for error in errors:
            err_status = error.get("status")
            err_detail = error.get("detail")
            logger.error(f"{err_status} - {err_detail}", 1)

    def __getJson(self):
        logger.info("Fetching API response...")

        cacheKey = f"{self.kind}:{self.id}:{self.storefront}"

        if not self.noCache:
            resCached = cache.get(cacheKey)
            if resCached is not None:
                logger.info("Using the response found in cache...")
                return resCached

        apiUrl = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'

        if self.kind == "album" or self.kind == "song":
            params = {
                'extend': 'editorialArtwork,editorialVideo',
                'include[songs]': 'albums,lyrics',
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

        if not self.noCache:
            if self.mediaUserToken:
                if not "errors" in response:
                    cache.set(cacheKey, response)
        
        return response
    
    def __getTs(self, ts):
        ts = ts.replace('s', '')
        secs = float(ts.split(':')[-1])

        if ":" in ts: mins = ts.split(':')[-2]
        else: mins = 0

        if self.syncPoints == 3: return f'{mins:0>2}:{secs:06.3f}'
        elif self.syncPoints == 2: return f'{mins:0>2}:{secs:05.2f}'
    
    def __getLyrics(self, ttml):
        ttml = BeautifulSoup(ttml, "lxml")

        songwriters = []
        lyrics = []
        timeSyncedLyrics = []

        songwriter = ttml.find_all("songwriter")
        if len(songwriter) > 0:
            for sw in songwriter:
                songwriters.append(sw.text)

        for line in ttml.find_all("p"):
            lyrics.append(line.text)
            if "span" in str(line):
                span = BeautifulSoup(str(line), "lxml")
                for s in span.find_all("span", attrs={'begin': True, 'end': True}):
                    begin = self.__getTs(s.get("begin"))
                    timeSyncedLyrics.append(f"[{begin}]{s.text}")
            else:
                begin = self.__getTs(line.get("begin"))
                timeSyncedLyrics.append(f"[{begin}]{line.text}")

        return {
            "songwriter": ', '.join(songwriters) if len(songwriters) > 0 else None,
            "lyrics": lyrics,
            "timeSyncedLyrics": timeSyncedLyrics
        }
    
    def __getAlbum(self):
        info = {}
        data = self.__getJson()
        if not "errors" in data:
            attr = data["data"][0]["attributes"]

            if "artwork" in attr: info["coverUrl"] = attr["artwork"].get("url").format(
                    w=attr["artwork"].get("width"),
                    h=attr["artwork"].get("height")
                )

            if self.anCover:
                if "editorialVideo" in attr:
                    if "motionDetailSquare" in attr["editorialVideo"]:
                        m3u8Url = attr["editorialVideo"]["motionDetailSquare"].get("video")
                        m3u8data = m3u8.load(m3u8Url).data

                        streamList = []

                        for i, variants in enumerate(m3u8data["playlists"]):
                            codec = variants["stream_info"].get("codecs")

                            if "avc" in codec: codec = "AVC"
                            elif "hvc" in codec: codec = "HEVC"

                            streamList.append({
                                "id": i,
                                "fps": variants["stream_info"].get("frame_rate"),
                                "codec": codec,
                                "range": variants["stream_info"].get("video_range"),
                                "bitrate": f'{round((variants["stream_info"].get("average_bandwidth"))/1000000, 2)} Mb/s',
                                "resolution": variants["stream_info"].get("resolution"),
                                "uri": variants.get("uri")
                            })

                        info["animatedCover"] = streamList

            trackList = []
            tracks = data["data"][0]["relationships"]["tracks"]["data"]

            for track in tracks:
                trackInfo = {}
                attr = track["attributes"]

                if track.get("type") == "songs":
                    if "albumName" in attr: trackInfo["album"] = attr.get("albumName")
                    if "genreNames" in attr: trackInfo["genre"] = ', '.join(attr.get("genreNames"))
                    if "trackNumber" in attr: trackInfo["tracknumber"] = attr.get("trackNumber")
                    if "releaseDate" in attr: trackInfo["releasedate"] = attr.get("releaseDate")
                    if "isrc" in attr: trackInfo["isrc"] = attr.get("isrc")
                    if "audioLocale" in attr: trackInfo["language"] = attr.get("audioLocale")
                    if "composerName" in attr: trackInfo["composer"] = attr.get("composerName")
                    if "discNumber" in attr: trackInfo["discnumber"] = attr.get("discNumber")
                    if "name" in attr: trackInfo["track"] = attr.get("name")
                    if "artistName" in attr: trackInfo["trackartist"] = attr.get("artistName")
                    if "contentRating" in attr: trackInfo["rating"] = attr.get("contentRating")

                    attr = track["relationships"]["albums"]["data"][0]["attributes"]

                    if "copyright" in attr: trackInfo["copyright"] = attr.get("copyright")
                    if "upc" in attr: trackInfo["upc"] = attr.get("upc")
                    if "recordLabel" in attr: trackInfo["recordlabel"] = attr.get("recordLabel")
                    if "trackCount" in attr: trackInfo["trackcount"] = attr.get("trackCount")
                    if "artistName" in attr: trackInfo["albumartist"] = attr.get("artistName")

                    if "lyrics" in track["relationships"]:
                        if len(track["relationships"]["lyrics"].get("data")) > 0:
                            trackInfo.update(self.__getLyrics(track["relationships"]["lyrics"]["data"][0]["attributes"].get("ttml")))

                    trackInfo["type"] = 1

                elif track.get("type") == "music-videos":
                    if "albumName" in attr: trackInfo["album"] = attr.get("albumName")
                    if "genreNames" in attr: trackInfo["genre"] = ', '.join(attr.get("genreNames"))
                    if "trackNumber" in attr: trackInfo["tracknumber"] = attr.get("trackNumber")
                    if "releaseDate" in attr: trackInfo["releasedate"] = attr.get("releaseDate")
                    if "isrc" in attr: trackInfo["isrc"] = attr.get("isrc")
                    if "name" in attr: trackInfo["track"] = attr.get("name")
                    if "artistName" in attr: trackInfo["trackartist"] = attr.get("artistName")
                    if "contentRating" in attr: trackInfo["rating"] = attr.get("contentRating")

                    trackInfo["type"] = 6

                trackList.append(trackInfo)
                
            info["tracks"] = trackList
            return info
        else: self.__getErrors(data.get("errors"))

    def __getSong(self):
        info = {}
        data = self.__getJson()
        if not "errors" in data:
            attr = data["data"][0]["relationships"]["albums"]["data"][0]["attributes"]

            if "artwork" in attr: info["coverUrl"] = attr["artwork"].get("url").format(
                    w=attr["artwork"].get("width"),
                    h=attr["artwork"].get("height")
                )

            if self.anCover:
                if "editorialVideo" in attr:
                    if "motionDetailSquare" in attr["editorialVideo"]:
                        m3u8Url = attr["editorialVideo"]["motionDetailSquare"].get("video")
                        m3u8data = m3u8.load(m3u8Url).data

                        streamList = []

                        for i, variants in enumerate(m3u8data["playlists"]):
                            codec = variants["stream_info"].get("codecs")

                            if "avc" in codec: codec = "AVC"
                            elif "hvc" in codec: codec = "HEVC"

                            streamList.append({
                                "id": i,
                                "fps": variants["stream_info"].get("frame_rate"),
                                "codec": codec,
                                "range": variants["stream_info"].get("video_range"),
                                "bitrate": f'{round((variants["stream_info"].get("average_bandwidth"))/1000000, 2)} Mb/s',
                                "resolution": variants["stream_info"].get("resolution"),
                                "uri": variants.get("uri")
                            })

                        info["animatedCover"] = streamList

            trackList = []
            tracks = data["data"]

            for track in tracks:
                trackInfo = {}
                attr = track["attributes"]

                if "albumName" in attr: trackInfo["album"] = attr.get("albumName")
                if "genreNames" in attr: trackInfo["genre"] = ', '.join(attr.get("genreNames"))
                if "trackNumber" in attr: trackInfo["tracknumber"] = attr.get("trackNumber")
                if "releaseDate" in attr: trackInfo["releasedate"] = attr.get("releaseDate")
                if "isrc" in attr: trackInfo["isrc"] = attr.get("isrc")
                if "audioLocale" in attr: trackInfo["language"] = attr.get("audioLocale")
                if "composerName" in attr: trackInfo["composer"] = attr.get("composerName")
                if "discNumber" in attr: trackInfo["discnumber"] = attr.get("discNumber")
                if "name" in attr: trackInfo["track"] = attr.get("name")
                if "artistName" in attr: trackInfo["trackartist"] = attr.get("artistName")
                if "contentRating" in attr: trackInfo["rating"] = attr.get("contentRating")

                attr = track["relationships"]["albums"]["data"][0]["attributes"]

                if "copyright" in attr: trackInfo["copyright"] = attr.get("copyright")
                if "upc" in attr: trackInfo["upc"] = attr.get("upc")
                if "recordLabel" in attr: trackInfo["recordlabel"] = attr.get("recordLabel")
                if "trackCount" in attr: trackInfo["trackcount"] = attr.get("trackCount")
                if "artistName" in attr: trackInfo["albumartist"] = attr.get("artistName")

                if "lyrics" in track["relationships"]:
                    if len(track["relationships"]["lyrics"].get("data")) > 0:
                        trackInfo.update(self.__getLyrics(track["relationships"]["lyrics"]["data"][0]["attributes"].get("ttml")))

                trackInfo["type"] = 1

                trackList.append(trackInfo)
                
            info["tracks"] = trackList
            return info
        else: self.__getErrors(data.get("errors"))

    def __getMusicVideo(self):
        info = {}
        data = self.__getJson()
        if not "errors" in data:
            trackInfo = {}
            attr = data["data"][0]["attributes"]

            if "genreNames" in attr: trackInfo["genre"] = ', '.join(attr.get("genreNames"))
            if "releaseDate" in attr: trackInfo["releasedate"] = attr.get("releaseDate")
            if "isrc" in attr: trackInfo["isrc"] = attr.get("isrc")
            if "name" in attr: trackInfo["track"] = attr.get("name")
            if "artistName" in attr: trackInfo["trackartist"] = attr.get("artistName")
            if "contentRating" in attr: trackInfo["rating"] = attr.get("contentRating")

            trackInfo["type"] = 6

            info["tracks"] = [trackInfo]
            return info
        else: self.__getErrors(data.get("errors"))

    def getInfo(self, url):
        self.__getUrl(url)
        if self.kind == "album":
            return self.__getAlbum()
        elif self.kind == "song":
            return self.__getSong()
        elif self.kind == "music-video":
            return self.__getMusicVideo()