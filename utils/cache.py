import os
import pickle

class Cache:
    def __init__(self, cacheDir):
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        self.cacheFile = os.path.join(cacheDir, "cache.bin")
        if not os.path.exists(self.cacheFile):
            cache = {
                "type": "cache"
            }
            with open(self.cacheFile, 'wb') as file:
                pickle.dump(cache, file)

    def get(self, key):
        with open(self.cacheFile, 'rb') as file:
            cache = pickle.load(file)
        return cache.get(key)

    def set(self, key, value):
        with open(self.cacheFile, 'rb') as file:
            cache = pickle.load(file)
        cache[key] = value
        with open(self.cacheFile, 'wb') as file:
            pickle.dump(cache, file)

    def delete(self, key):
        with open(self.cacheFile, 'rb') as file:
            cache = pickle.load(file)
        if key in cache:
            del cache[key]
        with open(self.cacheFile, 'wb') as file:
            pickle.dump(cache, file)