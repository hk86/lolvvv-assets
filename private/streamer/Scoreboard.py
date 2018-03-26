import asyncio

from pprint import pprint
from syncer import sync #pip install syncer
from pyppeteer import launch #pip install pyppeteer # 0.0.16

class Scoreboard:

    def __init__(self):
        self._browser = sync(launch())
        self._page = sync(self._browser.newPage())
        sync(self._page.goto('http://www.lolvvv.com/live?disableStream&disableSidebar', {'timeout': 0}))
        sync(self._page.setViewport({'width': 1150, 'height': 620}))

    def get(self):
        image_path = 'lolvvv_active_match.png'
        sync(self._page.reload())
        sync(self._page.screenshot({
                    'path': image_path,
                    'clip': {'x': 7, 'y': 118, 'width': 1137, 'height': 487}
                    }))
        return open(image_path, 'rb+')

    def __exit__(self):
        sync(self._browser.close())