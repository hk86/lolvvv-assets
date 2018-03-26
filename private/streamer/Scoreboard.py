import asyncio

from syncer import sync #pip install syncer
from pyppeteer import launch #pip install pyppeteer # 0.0.16

class Scoreboard:

    def __init__(self):
        self._browser = sync(launch())
        self._page = sync(self._browser.newPage())
        sync(self._page.goto('http://www.lolvvv.com/live?disableStream&disableSidebar', {'timeout': 0}))
        sync(self._page.setViewport({'width': 1150, 'height': 620}))

    def get(self):
        return sync(self._page.screenshot({
                    'path': 'lolvvv_active_match.png',
                    'clip': {'x': 7, 'y': 118, 'width': 1137, 'height': 487}
                    }))

    def __exit__(self):
        sync(self._browser.close())