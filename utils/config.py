import os
import pickle

class Config(object):
    def __init__(self, cache: str):
        if not os.path.exists(cache):
            os.makedirs(cache)
        
        self.__config = os.path.join(cache, "config.bin")

        if not os.path.exists(self.__config):
            mediaUserToken = input("\n\tmediaUserToken: ")
            
            print()

            __config = {
                "contentType": "configuration",
                "mediaUserToken": mediaUserToken
            }

            with open(self.__config, 'wb') as c:
                pickle.dump(__config, c)

    def get(self, key):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)
        return __config.get(key)

    def set(self, key, value):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)

        __config[key] = value

        with open(self.__config, 'wb') as c:
            pickle.dump(__config, c)

    def delete(self, key):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)

        if key in __config:
            del __config[key]

        with open(self.__config, 'wb') as c:
            pickle.dump(__config, c)