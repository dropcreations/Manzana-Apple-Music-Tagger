import re
import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from utils import Cache
from utils import Config
from utils import logger

from api.parse import parseJson

class AppleMusic(object):
    def __init__(self, cache, sync, skipVideo):
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

        self.__cache = Cache(cache)
        self.__config = Config(cache)

        self.sync = int(sync)
        self.skipVideo = skipVideo

        self.__accessToken()
        self.__mediaUserToken()

    def __checkUrl(self, url):
        try:
            urlopen(url)
            return True
        except (URLError, HTTPError):
            return False

    def __getUrl(self, url):
        __url = urlparse(url)

        if not __url.scheme:
            url = f"https://{url}"

        if __url.netloc == "music.apple.com":
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
        accessToken = self.__cache.get("accessToken")

        if not accessToken:
            logger.info("Fetching access token from web...")
            response = requests.get('https://music.apple.com/us/browse')

            if response.status_code != 200:
                logger.error("Failed to get music.apple.com! Please re-try...", 1)
            
            content = BeautifulSoup(response.text, "html.parser")

            indexJs = content.find(
                "script",
                attrs={
                    'type': 'module',
                    'crossorigin': True,
                    'src': True
                }
            ).get('src')

            response = requests.get(f'https://music.apple.com{indexJs}')

            if response.status_code != 200:
                logger.error("Failed to get JavaScript library! Please re-try...", 1)

            accessToken = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            self.__cache.set("accessToken", accessToken)
        else:
            logger.info("Checking access token found in cache...")

            self.session.headers.update(
                {
                    'authorization': f'Bearer {accessToken}'
                }
            )

            response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")

            if response.text == '':
                logger.info("Access token found in cache is expired!")

                self.__cache.delete("access_token")
                self.__accessToken()
        
        self.session.headers.update(
            {
                'authorization': f'Bearer {accessToken}'
            }
        )

    def __mediaUserToken(self):
        if self.__config.get('mediaUserToken'):
            logger.info("Checking media-user-token...")

            self.session.headers.update(
                {
                    "media-user-token": self.__config.get("mediaUserToken")
                }
            )

            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")

            if response.status_code == 200:
                response = json.loads(response.text)

                self.storefront = response["data"][0]["id"]
                self.language = response["data"][0]["attributes"]["defaultLanguageTag"]

                self.session.headers.update(
                    {
                        'accept-language': f'{self.language},en;q=0.9'
                    }
                )

                self.isMediaUserToken = True
            else:
                logger.error("Invalid media-user-token! Passing over the user subscription...")
                self.__config.delete('mediaUserToken')
        else:
            self.storefront = 'us'
            self.language = 'en-US'
            self.isMediaUserToken = False

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
        __cache = self.__cache.get(cacheKey)

        if __cache:
            logger.info("Using the previous response found in cache...")
            return __cache

        apiUrl = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'

        if self.kind == "album" or self.kind == "song":
            params = {
                'extend': 'editorialVideo',
                'include[songs]': 'albums,lyrics,credits',
                'l': f'{self.language}'
            }

        elif self.kind == "music-video":
            params = {
                'l': f'{self.language}'
            }

        self.session.params = params

        response = json.loads(
            self.session.get(
                apiUrl
            ).text
        )

        if not "errors" in response:
            self.__cache.set(cacheKey, response)
            return response
        else:
            self.__getErrors(response)

    def getInfo(self, url):
        self.__getUrl(url)

        if self.kind == "album":
            return parseJson(
                self.__getJson()["data"][0]["relationships"]["tracks"]["data"],
                self.sync,
                self.skipVideo
            )
        elif self.kind == "song":
            return parseJson(
                self.__getJson()["data"],
                self.sync
            )
        elif self.kind == "music-video":
            return parseJson(
                self.__getJson()["data"],
                self.sync
            )