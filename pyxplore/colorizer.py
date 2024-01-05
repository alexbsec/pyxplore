from colorama import Fore, Style, init
import sys

init(autoreset=True)

class ColorOutput:
    def __init__(self):
        self.current_color = Fore.WHITE

    def print(self, text):
        sys.stdout.buffer.write((self.current_color + text + Fore.RESET).encode('utf-8'))

    def printl(self, text, end=None):
        print(self.current_color + text + Fore.RESET, end=end)

    def __getattr__(self, color):
        # Check if the color is a valid Colorama foreground color
        if hasattr(Fore, color.upper()):
            self.current_color = getattr(Fore, color.upper())
        else:
            raise AttributeError(f"No such color: {color}")
        return self