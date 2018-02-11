# coding: utf-8


import subprocess
import time
import datetime

import pprint
import pyautogui
import pymongo

from LoL import *
from Database import Database
from LiveMatch import LiveMatch
from Twitch import Twitch
    

if __name__ == "__main__":

    db = Database('mongodb://root:ZTgh67gth1@10.8.0.14:27017/meteor?authSource=admin')
    
    twitch = Twitch('d8kxeyceb97glconsuj9at66c9lq7zfdu7r2rdonn3u5642mwj')
    
    while True:
        match = db.getTopRatedLiveMatch()
        if match:
            live_match = LiveMatch(match)
            db.setStreamingParams(live_match.getGameId(), live_match.getPlatform())

            title = live_match.getTitle()
            
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            print('streaming now: ' + title)
            
            twitch.set_title(title)
        
            LoL_start_spectate(live_match.getUrl(), live_match.getGameId(), live_match.getEncKey(), live_match.getPlatform())
        
            # wait for lol loaded
            time.sleep(45)
            # modify ui
            LoL_modify_ui()
        
            # start obs here
        
            while db.matchStillRunning(live_match.getGameId()):
                time.sleep(10) # sleep for 10 seconds
            
            while True:
                time.sleep(10) # sleep for 10 seconds
                match = db.getMatch(live_match.getGameId())
                if match:
                    # The match is over if it could be found in matches
                    match_finished_time = match['gameEnding']/1000
                    timediff_s = ( datetime.datetime.fromtimestamp(match_finished_time) - datetime.datetime.now() ).total_seconds() + 180
                    if timediff_s > 0:
                        time.sleep(timediff_s)
                
                    print('Timediff ' + str(timediff_s) + ' is over')
                    break
            
            
            LoL_stop()
        else:
            print('couldnt\'t find match')
            time.sleep(10) # sleep for 10 seconds



    #subprocess.call(['shutdown', '-t 0', '-r', '-f'])