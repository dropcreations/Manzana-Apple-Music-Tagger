import os
import json
from rich.console import Console

console = Console()

class Config():
    def __init__(self, configJson, cache):
        self.config_json = configJson
        self.cache_dir = cache

        if os.path.exists(self.config_json):
            with open(self.config_json, "r") as j:
                self.config = json.load(j)
        else:
            c = {
                "mediaUserToken": ""
            }
            with open(self.config_json, "w") as j:
                json.dump(c, j, indent=4)

    def init(self):
        console.print("[yellow bold]If you have an Apple Music subscription, enter your [green]media-user-token[/] to use your subscription.[/]\n")
        __mut = input("   media-user-token: ")
        c = {
            "mediaUserToken": __mut
        }
        with open(self.config_json, "w") as j:
            json.dump(c, j, indent=4)

    def reset(self):
        if os.path.exists(self.config_json): os.remove(self.config_json)
        if os.path.exists(self.cache_dir):
            for item in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, item))
            os.removedirs(self.cache_dir)
        c = {
            "mediaUserToken": ""
        }
        with open(self.config_json, "w") as j:
            json.dump(c, j, indent=4)
        console.print("[yellow bold]Reset completed.[/]")

    def mediaUserToken(self):
        with open(self.config_json, 'r') as j:
            j = json.load(j)
            return j["mediaUserToken"]