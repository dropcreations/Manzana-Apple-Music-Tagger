import sys

from datetime import datetime
from rich.console import Console

class Logger:
    def __init__(self):
        self.__console = Console()

    def info(
            self,
            log: str,
            exit: int = 0,
            inline: bool = False
        ):

        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][ManzanaCore][/] [deep_sky_blue1]INFO:[/] [bold bright_white]{log}[/]"
        
        if inline: self.__console.print(log, end='\r')
        else: self.__console.print(log)

        if exit == 1:
            sys.exit()

    def error(
            self,
            log: str,
            exit: int = 0,
            inline: bool = False
        ):

        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][ManzanaCore][/] [bold red]ERROR:[/] [bold bright_white]{log}[/]"
        
        if inline: self.__console.print(log, end='\r')
        else: self.__console.print(log)

        if exit == 1:
            sys.exit()

    def warning(
            self,
            log: str,
            exit: int = 0,
            inline: bool = False
        ):

        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        log = f"[bold green][{now}][/] [bold yellow][ManzanaCore][/] [bold red]WARNING:[/] [bold bright_white]{log}[/]"
        
        if inline: self.__console.print(log, end='\r')
        else: self.__console.print(log)

        if exit == 1:
            sys.exit()

logger = Logger()