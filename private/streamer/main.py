# coding: utf-8


import subprocess
import time
import datetime
import logging
import sys

import pprint
import pyautogui
import pymongo

from LoL import *
from OBS import *
from ServerSystem import *
from Database import Database
from LiveMatch import LiveMatch
from Twitch import Twitch
    

if __name__ == "__main__":

    logger = logging.getLogger('STREAM')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    fh = logging.FileHandler('streaming.log')
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    db = Database('mongodb://root:ZTgh67gth1@10.8.0.6:27017/meteor?authSource=admin',
                  '10.8.0.1:27017')
    
    twitch = Twitch('d8kxeyceb97glconsuj9at66c9lq7zfdu7r2rdonn3u5642mwj')
    
    sys = ServerSystem()

    obs = OBS(sys)

    lol = LeagueOfLegends(sys, logger)
    try:
        obs.startStreaming()
        ii = 0
        maxStreamingMatches = 50
        while ii < maxStreamingMatches:
            match = db.getTopRatedLiveMatch()
            if match:
                live_match = LiveMatch(match)
                db.setStreamingParams(live_match.getGameId(), live_match.getPlatform())
                obs.showUpcomingmatchScene()

                title = live_match.getTitle(db)
            
                logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                logger.info('streaming now: ' + title)
            
                twitch.set_title(title)
        
                lol.start_spectate(live_match.getUrl(), live_match.getGameId(), live_match.getEncKey(), live_match.getPlatform())
        
                # wait for lol loaded
                obs.countdown(35)
                
                lol.modify_ui()
                lol.startShowMoney(50, 10)
                obs.showIngameScene()

                obs.setPros(live_match.getPros(), db)
            
                obs.startDiashow(20)

                time.sleep(30)

                lol.checkRunning(obs)
        
                while db.matchStillRunning(live_match.getGameId(), live_match.getPlatform()):
                    time.sleep(10) # sleep for 10 seconds
            
                lol.stopPending(180,5)
            
                obs.stopDiashow()
                lol.stopShowMoney()

                ii = ii + 1
            else:
                logger.info('couldnt\'t find match')
                time.sleep(10) # sleep for 10 seconds
                ii = ii + 0.0005
    except:
        logger.exception('Exception in main.py')
        raise
    finally:
        for handler in logger.handlers:
            handler.close()
            logger.removeFilter(handler)
        sys.reboot()