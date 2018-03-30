# coding: utf-8


import subprocess
import time
import datetime
import logging
import sys

import pprint
import pyautogui
import pymongo

from LoL import LeagueOfLegends
from OBS import OBS
from ServerSystem import ServerSystem
from Database import Database
from LiveMatch import LiveMatch
from Twitch import Twitch
from Twitter import Twitter
from Instagram import Instagram
    

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

    db = Database('mongodb://root:ZTgh67gth1@10.8.0.6:27017/meteor?authSource=admin')
    
    twitch = Twitch('d8kxeyceb97glconsuj9at66c9lq7zfdu7r2rdonn3u5642mwj')
    
    sys = ServerSystem()

    obs = OBS(sys)

    lol = LeagueOfLegends(sys, logger, obs)

    scoreboard = Scoreboard()

    twitter = Twitter(db, logger, scoreboard)
    insta = Instagram(db, scoreboard)

    try:
        ii = 0
        maxStreamingMatches = 50
        while ii < maxStreamingMatches:
            match = db.getTopRatedLiveMatch()
            if match:
                live_match = LiveMatch(match)
                db.setStreamingParams(live_match.getGameId(), live_match.getPlatform())
                obs.showUpcomingmatchScene(True)
                obs.startStreaming()

                title = live_match.getTwitchTitle(db)
            
                logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                logger.info('streaming now: ' + title)
            
                twitch.set_title(title)
                logger.debug('title')
        
                lol.start_spectate(live_match.getUrl(), live_match.getGameId(), live_match.getEncKey(), live_match.getPlatform())
                logger.debug('start spectate')
        
                # wait for lol loaded

                obs.setPros(live_match.getPros(), db)
                # twitter.tweet(live_match)
                
                obs.countdown(35)
                
                lol.modify_ui()
                lol.startShowMoney(50, 10)
                obs.showUpcomingmatchScene(False)
            
                obs.startDiashow(20)
                # workaround
                twitter.tweeting(live_match)
                insta.generateArticle(live_match)
                time.sleep(30)

                lol.checkRunning()
        
                logger.debug('wait for running match')
                while db.matchStillRunning(live_match.getGameId(), live_match.getPlatform()):
                    time.sleep(10) # sleep for 10 seconds
            
                logger.debug('stop pending')
                lol.stopPending(180,5)
            
                logger.debug('stop money, diashow and ')
                db.setStreamingMatchEnd(live_match.getGameId(), live_match.getPlatform())
                obs.stopDiashow()
                lol.stopShowMoney()

                ii = ii + 1
            else:
                obs.stopStreaming()
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