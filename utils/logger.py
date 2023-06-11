import sys

from datetime import datetime
from rich.console import Console

class Logger:
    def __init__(self, name):
        self.name = name
        self.__console = Console()

    def info(self, log):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][{self.name}][/] [deep_sky_blue1]INFO:[/] [bold bright_white]{log}[/]"
        self.__console.print(log)

    def error(self, log, exit=0):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][{self.name}][/] [bold red]ERROR:[/] [bold bright_white]{log}[/]"
        self.__console.print(log)

        if exit == 1:
            sys.exit()

    def warning(self, log, exit=0):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][{self.name}][/] [deep_sky_blue1]WARNING:[/] [bold bright_white]{log}[/]"
        self.__console.print(log)

        if exit == 1:
            sys.exit()