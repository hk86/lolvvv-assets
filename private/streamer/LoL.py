import subprocess
import time
import datetime

import pyautogui #pip install pyautogui

from DirectInput import *
from Interval import *

class LeagueOfLegends:

    def __init__(self, system, logger, obs):
        self.sys = system
        self._logger = logger
        self._obs = obs

    def start_spectate (self, url, gameId, encryptionKey, platformId):
        subprocess.call(['spectate.bat', url, str(gameId), encryptionKey, platformId])

    def modify_ui(self):
        toggleKey(0x18) #toggle u
        toggleKey(0x16) #toggle o

    def startShowMoney(self, interval_s, duration_s):
        self._showMoneyDuration_s = duration_s
        self._interval = Interval(interval_s, self._showMoney)
        self._interval.start()

    def stopShowMoney(self):
        self._interval.stop()

    def _showMoney(self):
        toggleKey(0x2D) #toggle x
        time.sleep(self._showMoneyDuration_s)
        toggleKey(0x2D) #toggle x

    def stop(self):
        self.sys.terminate('League of Legends.exe')
        
    def _getCurrentTime(self):
        return datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

    def checkRunning(self):
        if (pyautogui.locateCenterOnScreen('PendingLoL.png')):
            cur_time = self._getCurrentTime()
            pyautogui.screenshot('notRunning' + cur_time + '.png')
            self._obs.stopStreaming()
            self.stop()
            subprocess.call(['updateLoL.bat'])
            time.sleep(300) # wait for updating
            raise Exception('Couldnt start LoL')
        elif (pyautogui.locateCenterOnScreen('lolCrashed.png')) or (pyautogui.locateCenterOnScreen('bugsplat.png')):
            self._obs.stopStreaming()
            self.stop()
            raise Exception('LoL Crashed')

    def stopPending(self, timeout_s, interval_s):
        trys = int(timeout_s/interval_s)
        if (interval_s > 4):
            interval_s = interval_s - 4 #time for locate on screen

        stop_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout_s)

        while True:
            if (pyautogui.locateCenterOnScreen('Continue.png')):
                break
            elif (pyautogui.locateCenterOnScreen('GameOver.png')):
                break
            elif (pyautogui.locateCenterOnScreen('dataUnavailable.png')):
                self._logger.warning('DATAUNAVAILBLE AT ' + self._getCurrentTime())
                break
            elif (pyautogui.locateCenterOnScreen('bugsplat.png')):
                self._obs.stopStreaming()
                self.stop()
                raise Exception('LoL Crashed')
            else:
                time.sleep(interval_s)
                if datetime.datetime.now() > stop_time:
                    cur_time = self._getCurrentTime()
                    self._logger.warning('NO EXIT AT ' + cur_time)
                    pyautogui.screenshot('noExit' + cur_time + '.png')
                    break
        self.stop()