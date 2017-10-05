import itertools
import sys
#import urlparse -(python2)
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, urlsplit, urlencode

import os
import re
import pickle
import zlib

import urllib.request as req
#from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from urllib.error import URLError 
from bs4 import BeautifulSoup
import time


userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

#custom request handler
class myReq(req.HTTPHandler):
    def http_request(self, req):
        req.headers["myHeader"] = userAgent
        return super().http_request(req)

opener = req.build_opener(myReq())
req.install_opener(opener)


class Downloader:
    def __init__(self, delay=2, user_agent=userAgent, num_retries=2, cache=None):
    #def __init__(self, delay=2, data=None, user_agent=userAgent, num_retries=2, cache=None):
        self.throttle = Throttle(delay)
        #self.data = data
        self.user_agent = user_agent
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url, data=None, doctype='html', filename="downloaded_file"):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                #url not in cache
                pass
            else:
                if self.num_retries > 0 and result['code'] == None or 500 <= result['code'] < 600:
                    #server error -> ignore cached data and redownload
                    result = None
        if result is None:
            self.throttle.wait(url)
            #headers = {'User-agent': self.user_agent}
            #fdata = {'CIK': data}
            if data == None:
                result = self.download(url, num_retries=self.num_retries, doctype=doctype, filename=filename)
                #result = self.download(url, headers, num_retries=self.num_retries)
            else:
                #byteData = data.encode()
                #print(type(byteData))
                #encoded_data = urlencode(byteData).encode('utf-8')
                encoded_data = urlencode(data).encode('utf-8')
                print(encoded_data)
                result = self.download(url, encoded_data, num_retries=self.num_retries, doctype=doctype, filename=filename)
                #result = self.download(url, encoded_data, headers, num_retries=self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result
        

    def download(self, url, data=None, user_agent={'User-agent':userAgent}, num_retries=2, doctype='html', filename='downloaded_file'):
        print("Downloading: ", url)
        print(data)
        request = req.Request(url,data,user_agent)
        #request = Request(url, data, user_agent)
        #download html
        if doctype == 'html':
            try:
                response = req.urlopen(request)
                #response = urlopen(request)
                html = response.read()
                code = response.code
            except Exception as e:
                print ('Download Error:', str(e))
                html = None
                if hasattr(e,'code'):
                    code = e.code
                    if num_retries > 0 and 500 <= code < 600:
                        #retry for 5xx error
                        return self._get(url, user_agent, num_retries-1)
        #download xml
        elif doctype == 'xml':
            try:
                #print("getting xml file with request: ",request)
                response = req.urlretrieve(url,filename)#D(baseurl+path)
                #data = urlretrieve(request)#D(baseurl+path)
                #print("got: "+data)
            except Exception as e:
                print ('Download Error:', str(e))
                html = None
                if hasattr(e,'code'):
                    code = e.code
                    if num_retries > 0 and 500 <= code < 600:
                        #retry for 5xx error
                        return self._get(url, user_agent, num_retries-1, 'xml')
            print("file was downloaded to: "+filename)
            return response
        else:
            print("unsupported document type requested")
        return {'html': html, 'code': code}


class Throttle:
    def __init__(self, delay):
        #delay time
        self.delay = delay
        #timestamp of most recent domain access
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        #update access time
        self.domains[domain] = datetime.now()


