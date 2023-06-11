import time
import sys
from rich.console import Console

RED = "\x1b[1;31;40m"
YELLOW = "\x1b[1;33;40m"

console = Console()


def print_ai_message(message):
    console.print("\n(AI) > ", message, "\n", style="bold red")


def print_slow(s):
    for char in s:
        time.sleep(0.02)
        sys.stdout.write(char)
        sys.stdout.flush()
