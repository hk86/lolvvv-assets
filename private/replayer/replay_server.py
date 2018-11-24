# pip install Naked
from Naked.toolshed.shell import muterun_js

from threading import Thread

class ReplayServer(Thread):

    def run(self):
        self._server_app = muterun_js('app.js')

    def stop(self):
        self._tstate_lock.release_lock()
        self._stop()