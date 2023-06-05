import os
import sys
import pickle
import colorama
from colorama import Fore
from datetime import datetime

colorama.init(autoreset=True)

class Logger:
    def __init__(self, name):
        self.name = name

    def info(self, quote):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        log = Fore.LIGHTGREEN_EX + f"[{current_time}] " + Fore.LIGHTYELLOW_EX + f"[{self.name}] " + Fore.LIGHTBLACK_EX + "INFO: " + Fore.LIGHTWHITE_EX + f"{quote}"
        print(log)

    def error(self, quote, exit=0):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        log = Fore.LIGHTGREEN_EX + f"[{current_time}] " + Fore.LIGHTYELLOW_EX + f"[{self.name}] " + Fore.LIGHTRED_EX + "ERROR: " + Fore.LIGHTWHITE_EX + f"{quote}"
        print(log)
        if exit == 1: sys.exit()

    def warning(self, quote, exit=0):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        log = Fore.LIGHTGREEN_EX + f"[{current_time}] " + Fore.LIGHTYELLOW_EX + f"[{self.name}] " + Fore.LIGHTBLACK_EX + "WARNING: " + Fore.LIGHTWHITE_EX + f"{quote}"
        print(log)
        if exit == 1: sys.exit()

class Cache:
    def __init__(self, cache_dir):
        self.cache_file = os.path.join(cache_dir, "cache.bin")
        if not os.path.exists(self.cache_file):
            cache = {
                "type": "cache"
            }
            with open(self.cache_file, 'wb') as file:
                pickle.dump(cache, file)

    def get(self, key):
        with open(self.cache_file, 'rb') as file:
            cache = pickle.load(file)
        return cache.get(key)

    def set(self, key, value):
        with open(self.cache_file, 'rb') as file:
            cache = pickle.load(file)
        cache[key] = value
        with open(self.cache_file, 'wb') as file:
            pickle.dump(cache, file)

    def delete(self, key):
        with open(self.cache_file, 'rb') as file:
            cache = pickle.load(file)
        if key in cache:
            del cache[key]
        with open(self.cache_file, 'wb') as file:
            pickle.dump(cache, file)