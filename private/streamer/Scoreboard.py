import asyncio

from pprint import pprint
from syncer import sync #pip install syncer
from pyppeteer import launch #pip install pyppeteer # 0.0.16

class Scoreboard:

    def __init__(self):
        self._browser = sync(launch())
        self._pageForTwitter = sync(self._browser.newPage())
        sync(self._pageForTwitter.goto('http://www.lolvvv.com/live?disableStream&disableSidebar', {'timeout': 0}))
        sync(self._pageForTwitter.setViewport({'width': 1150, 'height': 620}))
        
        self._pageForInsta = sync(self._browser.newPage())
        sync(self._pageForInsta.goto('https://www.lolvvv.com/special/instagram/active-match', {'timeout': 0}))
        sync(self._pageForInsta.setViewport({'width': 1600, 'height': 1300}))
        

    def get(self):
        image_path = 'lolvvv_active_match.png'
        sync(self._pageForTwitter.reload())
        sync(self._pageForTwitter.screenshot({
                    'path': image_path,
                    'clip': {'x': 7, 'y': 118, 'width': 1137, 'height': 487}
                    }))
        return open(image_path, 'rb+')

    def getForInsta(self):
        image_path = 'lolvvv_scoreboard_insta.jpg'
        sync(self._pageForInsta.reload())
        sync(self._pageForInsta.screenshot({
                    'path': image_path,
                    'clip': {'x': 443, 'y': 65, 'width': 714, 'height': 714}
                    }))
        return image_path

    def __exit__(self):
        sync(self._browser.close())