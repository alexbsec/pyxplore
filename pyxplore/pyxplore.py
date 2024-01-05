from . import xrequests, colorizer
import argparse
import asyncio
import re
import time

def safe_convert_to_i(value):
    try:
        return int(value)
    except ValueError:
        return None

def check_gcode_input(input):
    if isinstance(input, int):
        return input

    if isinstance(input, str):
        if re.match(r'^\d+$', input):
            return int(input)
        elif re.match(r'^[a-zA-Z]+$', input):
            return input
    
    return None

def check_gcode_status(input):
    if re.match(r'^\d{1,3}(,\d{3})*$', input):
        return True
    return False

def main():
    positional_arg_list = ["php", "asp", "aspx", "html", "config", "ui_config", "xml", "general", "simple", "js", "routes", "apache", "nginx", "custom"]
    co = colorizer.ColorOutput()
    parser = argparse.ArgumentParser(
        prog='PyXplore',
        description="Web Fuzzer"
    )

    parser.add_argument('mode', help="specify a positional argument: [php|asp|aspx|html|config|ui_config|massive|general|apache|nginx|js|routes|custom]")
    parser.add_argument('-u', '--url', type=str)
    parser.add_argument('-g', '--grep-code')
    parser.add_argument('-o', '--output', type=str)
    parser.add_argument('-d', '--delay', type=int)
    parser.add_argument('-S', '--use-small', dest="use_small", action='store_true')
    parser.add_argument('-s', '--silent', action='store_true')
    parser.add_argument('-w', '--wordlist', default=None)
    parser.add_argument('-x', '--ext', default="")
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--no-ssl', dest="no_ssl", action='store_true')
    parser.add_argument('--concurrent-count', dest="cc", default=10, type=int)
    args = parser.parse_args()

    url = args.url
    gcode = args.grep_code
    output = args.output
    delay = args.delay if args.delay is not None else 0
    use_small = args.use_small
    silent = args.silent
    cc = args.cc
    mode = args.mode
    wordlist_path = args.wordlist
    wordlist = []
    no_ssl = args.no_ssl
    ext = args.ext
    verbose = args.verbose
    
    if url is None:
        co.yellow.printl("Missing URL flag '-u'")
        exit(1)

    if url.startswith("http://"):
        no_ssl = True
    elif url.startswith("https://"):
        no_ssl = False

    if mode not in positional_arg_list:
        co.red.printl(f"Invalid mode '{mode}'")
        exit(1)

    if mode == "custom" and wordlist_path is None:
        co.red.printl(f"Custom mode requires your own wordlist, which was not provided. Please use -w for that")
        exit(1)
    elif mode == "custom":
        with open(wordlist_path, "r") as f:
            for line in f:
                wordlist.append(line.strip() + ext)


    if gcode is None:
        gcode = "200"

    gcode_check = check_gcode_input(gcode)
    if gcode_check is None:
        gcode_good = check_gcode_status(gcode)
        if not gcode_good:
            co.red.printl(f"Grep code format '{gcode}' does not match the expected.")
            exit(1)
        else:
            gcode = gcode.split(',')
            gcode = [safe_convert_to_i(item) for item in gcode]
            gcode = [item for item in gcode if item is not None]
    elif isinstance(gcode_check, int):
        gcode = [gcode_check]
    elif gcode != 'all':
        co.red.printl(f"Grep code format '{gcode}' does not match the expected.")
        exit(1)

    size = "small" if use_small else "large"
    use_https = True if not no_ssl else False
        
    co.red.printl(r'''
        __    __            __                               
        /  |  /  |          /  |                              
        $$ |  $$ |  ______  $$ |  ______    ______    ______  
        $$  \/$$/  /      \ $$ | /      \  /      \  /      \ 
         $$  $$<  /$$$$$$  |$$ |/$$$$$$  |/$$$$$$  |/$$$$$$  |
          $$$$  \ $$ |  $$ |$$ |$$ |  $$ |$$ |  $$/ $$    $$ |
         $$ /$$  |$$ |__$$ |$$ |$$ \__$$ |$$ |      $$$$$$$$/ 
        $$ |  $$ |$$    $$/ $$ |$$    $$/ $$ |      $$       |
        $$/   $$/ $$$$$$$/  $$/  $$$$$$/  $$/        $$$$$$$/ 
                  $$ |                                        
                  $$ |                                        
                  $$/         
''')
    co.green.printl("       v.0.1.0 - By alexbsec https://github.com/alexbsec")
    print("---------------------------------------------------------")
    time.sleep(1.5)
    co.white.printl("PARAMETERS:")
    print("---------------------------------------------------------")
    co.green.printl(f"PyXplore list mode:            {mode}")
    co.green.printl(f"Grep status code:              {gcode}")
    co.green.printl(f"Delay:                         {delay} ms")
    co.green.printl(f"Concurrent requests:           {cc} req/sec")
    co.green.printl(f"Output file:                   {output}")
    co.green.printl(f"Use https:                     {use_https}")
    co.green.printl(f"Host:                          {url}")
    co.green.printl("Starting to \033[1mXplore...\033[0m")
    time.sleep(1.5)

    if gcode == 'all':
        gcode = [100, 101, 102, 103, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 300,
        301, 302, 303, 304, 305, 306, 307, 308, 400, 401, 402, 403, 404, 405, 406,
        407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423,
        424, 426, 428, 429, 431, 451, 500, 501, 502, 503, 504, 505, 506, 507, 508,
        510, 511
      ]
        

        
    req = xrequests.XploreRequest(url, gcode, mode, output=output, size=size, delay=delay, use_https=use_https, wl=wordlist, cc=cc, verbosity=verbose)
    try:
        asyncio.run(req.fuzz())
    except KeyboardInterrupt:
        # Handle any additional cleanup here if necessary
        co.yellow.printl("Exiting...")
        exit(0)
    except asyncio.exceptions.CancelledError:
        co.red.printl("Cleanup failed. Exiting")
        exit(1)
            

if __name__ == '__main__':
    main()
