import re
import json
import requests

from urllib.parse import urlparse

from utils import Cache
from utils import Logger
from handler import checkUrl

from api.song import song
from api.album import album
from api.musicvideo import musicVideo

logger = Logger("AppleMusic")

HEADERS = {
    'content-type': 'application/json;charset=utf-8',
    'connection': 'keep-alive',
    'accept': 'application/json',
    'origin': 'https://music.apple.com',
    'referer': 'https://music.apple.com/',
    'accept-encoding': 'gzip, deflate, br',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

class AppleMusic(object):
    def __init__(self, cachedir: str, animartwork: bool, syncpoints: int, mediaUserToken = None):
        self.session = requests.Session()
        self.session.headers = HEADERS

        self.cache = Cache(cachedir)
        self.sync = syncpoints
        self.animartwork = animartwork
        self.mediaUserToken = mediaUserToken
        self.isMediaUserToken = False

        self.storefront = "us"
        self.language = "en-US"

        self.__accessToken()
        self.__mediaUserToken()

    def __getUrl(self, url):
        parsedUrl = urlparse(url)

        if not parsedUrl.scheme: url = f"https://{url}"
        if parsedUrl.netloc == "music.apple.com":
            if checkUrl(url):
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
        accessToken = self.cache.get("access_token")

        if not accessToken:
            logger.info("Fetching access token from web...")

            response = requests.get('https://music.apple.com/us/browse')
            if response.status_code != 200:
                logger.error("Failed to get music.apple.com! Please re-try...", 1)

            indexJs = re.search('(?<=index)(.*?)(?=\.js")', response.text).group(1)
            response = requests.get(f'https://music.apple.com/assets/index{indexJs}.js')
            if response.status_code != 200:
                logger.error("Failed to get js library! Please re-try...", 1)

            accessToken = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            self.cache.set("access_token", accessToken)
        else:
            logger.info("Checking access token found in cache...")

            self.session.headers.update(
                {
                    'authorization': f'Bearer {accessToken}'
                }
            )
            response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")

            if response.text == "":
                logger.info("Access token found in cache is expired!")

                self.cache.delete("access_token")
                self.__accessToken()
        
        self.session.headers.update(
            {
                'authorization': f'Bearer {accessToken}'
            }
        )

    def __mediaUserToken(self):
        if self.mediaUserToken:
            logger.info("Checking media-user-token...")

            self.session.headers.update(
                {
                    "media-user-token": self.mediaUserToken
                }
            )

            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")

            if response.status_code == 200:
                response = json.loads(response.text)

                self.storefront = response["data"][0].get("id")
                self.language = response["data"][0]["attributes"].get("defaultLanguageTag")

                self.session.headers.update(
                    {
                        'accept-language': f'{self.language},en;q=0.9'
                    }
                )
                self.isMediaUserToken = True
            else:
                logger.error("Invalid media-user-token!")

    def __getErrors(self, errors):
        if not isinstance(errors, list):
            errors = [errors]
        for error in errors:
            err_status = error.get("status")
            err_detail = error.get("detail")
            logger.error(f"{err_status} - {err_detail}", 1)

    def __getJson(self):
        logger.info("Fetching api response...")

        cacheKey = f"{self.id}:{self.storefront}"
        __cache = self.cache.get(cacheKey)
        if __cache:
            logger.info("Using the previous response found in cache...")
            return __cache

        apiUrl = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'

        if self.kind == "album" or self.kind == "song":
            params = {
                'extend': 'editorialArtwork,editorialVideo',
                'include[songs]': 'albums,lyrics',
                'l': f'{self.language}'
            }

        elif self.kind == "music-video":
            params = {
                'l': f'{self.language}'
            }

        self.session.params = params

        response = self.session.get(apiUrl)
        response = json.loads(response.text)

        if not "errors" in response:
            if self.mediaUserToken:
                self.cache.set(cacheKey, response)
            return response
        else: self.__getErrors(response)

    def getInfo(self, url):
        self.__getUrl(url)

        if self.kind == "album":
            return album(
                self.__getJson(),
                syncpoints=self.sync,
                animartwork=self.animartwork
            )
        elif self.kind == "song":
            return song(
                self.__getJson(),
                syncpoints=self.sync,
                animartwork=self.animartwork
            )
        elif self.kind == "music-video":
            return musicVideo(self.__getJson())