import requests
from . import colorizer
import time
import re

def coprint(text):
    co = colorizer.ColorOutput()
    match text:
        case _ if re.match(r"^2\d{2}$", text):
            co.green.print(text)
        case _ if re.match(r"^3\d{2}$", text):
            co.blue.print(text)
        case _ if re.match(r"^4\d{2}$", text):
            co.red.print(text)
        case _ if re.match(r"^5\d{2}$", text):
            co.red.print(text)
        case _:
            co.white.print(text)  # Default case if none of the above patterns match


class XploreRequest(requests.Session):
    WORDLISTS = {
                'php': {
                        'small': 'https://wordlists-cdn.assetnote.io/data/manual/phpmillion.txt',
                        'large': 'https://wordlists-cdn.assetnote.io/data/manual/php.txt'
                    },
                'asp': {
                        'small': 'https://wordlists-cdn.assetnote.io/data/manual/asp_lowercase.txt'
                    },
                'aspx': {
                        'small': 'https://wordlists-cdn.assetnote.io/data/manual/aspx_lowercase.txt'
                    }
            }

    def __init__(self, url, gcode, typ, output=None, size='small', delay=0, use_https=True, wl=None):
        # check url format
        super().__init__()
        if not (url.startswith('https://') or url.startswith('http://')):
            url = f"https://{url}" if use_https else f"http://{url}"
        
        if not url.endswith('/'):
            url += "/"
        
        self.url = url
        self.gcode = gcode
        self.output = output
        self.delay = delay
        self.use_ssl = use_https
        self.type = typ
        self.size = size
        self.co = colorizer.ColorOutput()
        self.wordlist = wl

    def fuzz(self):
        if self.type != "custom":
            wl_url = self.WORDLISTS[self.type][self.size]
            with self.get(wl_url, stream=True) as wl_res:
                wl_res.raise_for_status()
                try:
                    for line in wl_res.iter_lines(decode_unicode=True):
                        time.sleep(self.delay)
                        word = line.strip()
                        word = word[1:] if word.startswith('/') else word
                        url = f"{self.url}{word}"
                        res = self.get(url)
                        if res.status_code in self.gcode:
                            coprint(f"[{res.status_code}] ")
                            print(url)
                except KeyboardInterrupt:
                    print()
                    self.co.red.printl("Xplore terminated by user")
                    exit(0)
        else:
            try:
                for word in self.wordlist:
                    time.sleep(self.delay)
                    word = word[1:] if word.startswith('/') else word
                    url = f"{self.url}{word}"
                    res = self.get(url)
                    if res.status_code in self.gcode:
                        coprint(f"[{res.status_code}] ")
                        print(url)
            except KeyboardInterrupt:
                    print()
                    self.co.red.printl("Xplore terminated by user")
                    exit(0)

