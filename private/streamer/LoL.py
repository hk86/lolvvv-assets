import subprocess
import time

import pyautogui #pip install pyautogui

from DirectInput import *

class LeagueOfLegends:
    pass

    def __init__(self, system, logger):
        self.sys = system
        self._logger = logger

    def start_spectate (self, url, gameId, encryptionKey, platformId):
        subprocess.call(['spectate.bat', url, str(gameId), encryptionKey, platformId])

    def modify_ui(self):
        toggleKey(0x18) #toggle u
        toggleKey(0x16) #toggle o

    def stop(self):
        self.sys.terminate('League of Legends.exe')

    def checkRunning(self, obs):
        if (pyautogui.locateCenterOnScreen('PendingLoL.png')):
            self._logger.error('LoL is not running')
            obs.stop()
            LoL_stop()
            subprocess.call(['updateLoL.bat'])
            time.sleep(300) # wait for updating
            self.sys.reboot()

    def stopPending(self, timeout_s, interval_s):
        for ii in range(int(timeout_s/interval_s)):
            if (pyautogui.locateCenterOnScreen('Continue.png')):
                break
            else:
                time.sleep(interval_s)
        self.stop()