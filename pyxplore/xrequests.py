import requests
from . import colorizer
import time
import re
import json
import aiohttp
import asyncio
import async_timeout

class XploreRequest(requests.Session):
    WL_NAME = "wl-temp.txt"
    
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

    def __init__(self, url, gcode, typ, output=None, size='small', delay=0, use_https=True, wl=None, cc=10, verbosity=0):
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
        self.cc = cc
        self.verbosity = verbosity
        self.matches = 0
        
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
        
    async def make_request(self, session, word):
        try:
            word = word[1:] if word.startswith('/') else word
            url = f"{self.url}{word}"
            async with async_timeout.timeout(10):  # Set timeout for each request
                async with session.get(url) as res:
                    if res.status in self.gcode:
                        self.coprint(f"[{res.status}] ")
                        self.STATUS_DICT[res.status].append(url)
                        self.matches += 1
                        print(url)
            await asyncio.sleep(self.delay)  # Non-blocking sleep
        except ConnectionResetError:
            self.co.red.printl("Connection reset by peer")
            exit(1)
        except KeyboardInterrupt:
            print()
            self.co.red.printl("Xplore terminated by user")
            exit(0)
        except asyncio.CancelledError:
            if self.verbosity >= 1:
                self.co.yellow.printl(f"Task cancelled: {word}")
                if self.verbosity >= 2:
                    self.co.yellow.printl("Cleaning up next...")
            return
        except Exception as e:
            if self.verbosity >= 1:
                self.co.red.printl(f"{e}")
            return
            
    def save_to_output(self):
        with open(f"{self.output}.json", 'w') as jf:
            json.dump(self.STATUS_DICT, jf)
        
    async def fuzz(self):
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(self.cc)
            tasks = []

            async def sem_task(word, c):
                async with semaphore:
                    output = f"Progress: {c}/{len(self.wordlist)} payloads sent" if len(self.wordlist) > 0 else f"Progress: {c} payloads sent"
                    self.co.white.printl(output, end="\r")
                    await self.make_request(session, word)
                    
            if self.type != "custom":
                # Stream the wordlist and create tasks on-the-fly
                async with session.get(self.WORDLISTS[self.type][self.size], timeout=60) as res:
                    res.raise_for_status()
                    c = 0
                    async for line in res.content:
                        word = line.decode('utf-8').strip()
                        task = asyncio.create_task(sem_task(word, c))
                        tasks.append(task)
                        c += 1
            else:
                c = 0
                for word in self.wordlist:
                    task = asyncio.create_task(sem_task(word, c))
                    tasks.append(task)
                    c += 1
                    

            await asyncio.gather(*tasks, return_exceptions=True)
        
            
        self.co.white.printl(f"\nPyXplore fuzzing complete. Found {self.matches} pages")

        if self.output is not None:
            self.save_to_output()