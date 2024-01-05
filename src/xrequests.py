import requests
from . import colorizer
import time
import re
import json

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
    
    STATUS_DICT = {}

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
        
        for code in gcode:
            self.STATUS_DICT[code] = []
        
    def coprint(self, text):
        # Extract status code from the string
        match = re.search(r"\[(\d{3})\]", text)
        if match:
            status_code = match.group(1) 

            if re.match(r"^2\d{2}$", status_code):
                self.co.green.print(text)
            elif re.match(r"^3\d{2}$", status_code):
                self.co.blue.print(text)
            elif re.match(r"^4\d{2}$", status_code):
                self.co.red.print(text)
            elif re.match(r"^5\d{2}$", status_code):
                self.co.red.print(text)
            else:
                self.co.white.print(text)
        else:
            # Handle cases where the status code is not found
            self.co.white.print(text)
        
    def make_request(self, wl_res):
        try:
            for line in wl_res.iter_lines(decode_unicode=True):
                time.sleep(self.delay)
                word = line.strip()
                word = word[1:] if word.startswith('/') else word
                url = f"{self.url}{word}"
                res = self.get(url)
                if res.status_code in self.gcode:
                    self.coprint(f"[{res.status_code}] ")
                    self.STATUS_DICT[res.status_code].append(url)
                    print(url)
        except ConnectionResetError:
            self.co.red.printl("Connection reset by peer")
            exit(1)
        except KeyboardInterrupt:
            print()
            self.co.red.printl("Xplore terminated by user")
            exit(0)
            
    def make_custom_request(self):
        try:
            for word in self.wordlist:
                time.sleep(self.delay)
                word = word[1:] if word.startswith('/') else word
                url = f"{self.url}{word}"
                res = self.get(url)
                if res.status_code in self.gcode:
                    self.coprint(f"[{res.status_code}] ")
                    self.STATUS_DICT[res.status_code].append(url)
                    print(url)
        except ConnectionResetError:
            self.co.red.printl("Connection reset by peer")
            exit(1)
        except KeyboardInterrupt:
            print()
            self.co.red.printl("Xplore terminated by user")
            exit(0)
            
    def save_to_output(self):
        with open(f"{self.output}.json", 'w') as jf:
            json.dump(self.STATUS_DICT, jf)
        
    def fuzz(self):
        if self.type != "custom":
            wl_url = self.WORDLISTS[self.type][self.size]
            with self.get(wl_url, stream=True) as wl_res:
                wl_res.raise_for_status()
                self.make_request(wl_res)
        else:
            self.make_custom_request()
        
        if self.output is not None:
            self.save_to_output()

