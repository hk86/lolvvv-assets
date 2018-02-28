import subprocess
import time
import datetime

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
        
    def _getCurrentTime(self):
        return datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

    def checkRunning(self, obs):
        if (pyautogui.locateCenterOnScreen('PendingLoL.png')):
            cur_time = self._getCurrentTime()
            pyautogui.screenshot('notRunning' + cur_time + '.png')
            obs.stop()
            self.stop()
            subprocess.call(['updateLoL.bat'])
            time.sleep(300) # wait for updating
            raise Exception('Couldnt start LoL')

    def stopPending(self, timeout_s, interval_s):
        trys = int(timeout_s/interval_s)
        for ii in range(trys):
            if (pyautogui.locateCenterOnScreen('Continue.png')):
                break
            else:
                time.sleep(interval_s)
                if ii == (trys-1):
                    cur_time = self._getCurrentTime()
                    self._logger.warning('NO EXIT AT ' + cur_time)
                    pyautogui.screenshot('noExit' + cur_time + '.png')
        self.stop()