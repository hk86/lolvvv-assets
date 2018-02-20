# coding: utf-8


import subprocess
import time
import datetime

import pprint
import pyautogui
import pymongo

from LoL import *
from OBS import *
from Database import Database
from LiveMatch import LiveMatch
from Twitch import Twitch
    

if __name__ == "__main__":

    db = Database('mongodb://root:ZTgh67gth1@10.8.0.14:27017/meteor?authSource=admin',
                  '10.8.0.1:27017')
    
    twitch = Twitch('d8kxeyceb97glconsuj9at66c9lq7zfdu7r2rdonn3u5642mwj')
    
    obs = OBS()
    obs.start()
    
    while True:
        match = db.getTopRatedLiveMatch()
        if match:
            live_match = LiveMatch(match)
            db.setStreamingParams(live_match.getGameId(), live_match.getPlatform())

            title = live_match.getTitle(db)
            
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            print('streaming now: ' + title)
            
            twitch.set_title(title)
        
            LoL_start_spectate(live_match.getUrl(), live_match.getGameId(), live_match.getEncKey(), live_match.getPlatform())
        
            # wait for lol loaded
            time.sleep(45)

            LoL_modify_ui()

            obs.setPros(live_match.getPros(), db)
            
            obs.startDiashow(40)
        
        
            while db.matchStillRunning(live_match.getGameId(), live_match.getPlatform()):
                time.sleep(10) # sleep for 10 seconds
            
            print('live_match ends at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

            time.sleep(160) # spectator offset
            
            obs.stopDiashow()
            LoL_stop()
        else:
            print('couldnt\'t find match')
            time.sleep(10) # sleep for 10 seconds



    #subprocess.call(['shutdown', '-t 0', '-r', '-f'])