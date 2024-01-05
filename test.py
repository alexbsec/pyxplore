from src import xrequests

req = xrequests.XploreRequest("http://abc.com", [200], "php", "small", None, None, False)
req.fuzz()