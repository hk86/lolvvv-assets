# coding: utf-8


import subprocess
import time
import datetime

import pyautogui
import pymongo

from LiveMatch import LiveMatch
from Twitch import Twitch

def match_ended ( gameId, matches ):
	if matches.find({'gameId': gameId}).count() > 0:
		return True
	else:
		return False
	

if __name__ == "__main__":

	# connect to 'python' Database
	mc = pymongo.MongoClient('10.8.0.1', 27017)
	factdata = mc['factdata']
	staticdata = mc['staticdata']
	active_matches = factdata['matches_active']
	matches = factdata['matches']
	
	twitch = Twitch('d8kxeyceb97glconsuj9at66c9lq7zfdu7r2rdonn3u5642mwj')
	
	#while True:
		# Find match
		# ToDo: find top rated match
	match = active_matches.find_one({'platformId': 'EUW1'}, sort=[('gameLength', 1)])
	
	if match:
		live_match = LiveMatch(match)
		title = live_match.getTitle(staticdata)
		print('streaming now: ' + title)
		twitch.set_title(title)
		
		LoL_start_spectate(live_match.getUrl(), live_match.getGameId(), live_match.getEncKey(), live_match.getPlatform())
		
		# wait for lol loaded
		time.sleep(45)
		# modify ui
		LoL_modify_ui()
		
		# start obs here
		
		while live_match.stillRunning(active_matches):
			time.sleep(10) # sleep for 10 seconds
			
		while True:
			time.sleep(10) # sleep for 10 seconds
			if matches.find({'gameId': live_match.getGameId()}).count() > 0:
				# The match is over if it could be found in matches
				match_duration = matches.find_one({'gameId': live_match.getGameId()})['gameDuration']
				match_finished_time = match['gameStartTime']/1000 + match_duration
				timediff_s = ( datetime.datetime.fromtimestamp(match_finished_time) - datetime.datetime.now() ).total_seconds() + 180
				if timediff_s > 0:
					time.sleep(timediff_s)
				
				print('Timediff ' + str(timediff_s) + ' is over')
				break
			elif pyautogui.locateCenterOnScreen('Continue.png') is not None:
				# The match is of over if there is the 'Continue' button on the screen
				print('Continue button found')
				break
			
			
		LoL_stop()
	else:
		print('couldnt\'t find match')
		time.sleep(10) # sleep for 10 seconds



	#subprocess.call(['shutdown', '-t 0', '-r', '-f'])