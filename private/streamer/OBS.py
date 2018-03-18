import subprocess
import collections
import json
import os
import time
import threading
from pathlib import Path
from shutil import copyfile

from Interval import *

import platform

import websocket
import pprint # for debug

class OBS():
   
    def __init__(self, system, obs_path='C:\\Program Files (x86)\\obs-studio'):
        if platform.architecture()[0] == '64bit':
            arch='64bit'
            self.obs_exe='obs64.exe'
        else:
            arch='32bit'
            self.obs_exe='obs32.exe'

        self._sys = system

        # setup scene from git
        sceneName = 'obs_lolvvv_1080p.json'
        obs_scene = os.path.join(os.getenv('APPDATA'), 'obs-studio/basic/scenes', sceneName)
        copyfile(sceneName, obs_scene)

        _obs_path = os.path.join(obs_path, 'bin', arch)
        subprocess.Popen([os.path.join(_obs_path, self.obs_exe)], cwd=_obs_path)
        time.sleep(3) # wait for obs launching

        self._reconnectToObs()

        self._proTeam_props = self._getProperties('proteam_txt')
        self._proTeam_settings = self._getSettings('proteam_txt')
        self._pros_settings = self._getSettings('proplayer_img')
        self._proName_settings = self._getSettings('proplayername_txt')
        self._champion_settings = self._getSettings('championplayed_img')
        self._perk1_settings = self._getSettings('perks1_img')
        self._perk2_settings = self._getSettings('perks2_img')

        self._countdown_settings = self._getSettings('countdown_txt_up')

        self._upcomingSceneProp = []
        self._upcomingSceneProp.append(self._getProperties('backgroundfbtw_img_up'))
        self._upcomingSceneProp.append(self._getProperties('countdown_txt_up'))
        self._upcomingSceneProp.append(self._getProperties('facebook_logo_up'))
        self._upcomingSceneProp.append(self._getProperties('facebook_txt_up'))
        self._upcomingSceneProp.append(self._getProperties('lolvvv_logo_up'))
        self._upcomingSceneProp.append(self._getProperties('lolvvvlink_txt_up'))
        self._upcomingSceneProp.append(self._getProperties('scoreboard_browser_up'))
        self._upcomingSceneProp.append(self._getProperties('twitter_logo_up'))
        self._upcomingSceneProp.append(self._getProperties('twitter_txt_up'))
        self._upcomingSceneProp.append(self._getProperties('upcomingmatch_txt_up'))
        self._upcomingSceneProp.append(self._getProperties('wallpaper_img_up'))

    
    def _toObsPath(self, path):
        return Path(os.path.abspath(path)).as_posix()

    def _setupScene(self, pro):
        blueId = 100
        redId = 200

        blueCol = 13665569
        redCol = 2631899

        if pro['matchTeamId'] == blueId:
            txtColor = blueCol
        else:
            txtColor = redCol

        self._pros_settings['file'] = pro['pic']
        self._proName_settings['text'] = pro['name']
        self._proName_settings['color'] = txtColor
        self._champion_settings['file']=pro['champion']
        self._perk1_settings['file']=pro['perk1']
        self._perk2_settings['file']=pro['perk2']

        self._setSettings('proplayer_img', self._pros_settings)
        self._setSettings('proplayername_txt', self._proName_settings)
        self._setSettings('championplayed_img', self._champion_settings)
        self._setSettings('perks1_img', self._perk1_settings)
        self._setSettings('perks2_img', self._perk2_settings)

        if pro['team']:
            self._proTeam_settings['text'] = pro['team']
            self._proTeam_settings['color'] = txtColor
            self._setSettings('proteam_txt', self._proTeam_settings)
            self._proTeam_props['visible'] = True
            self._setProperties(self._proTeam_props)
        else:
            self._proTeam_props['visible'] = False
            self._setProperties(self._proTeam_props)

    def _reconnectToObs(self, url='ws://localhost:4444'):
        self._ws=None
        self._ws=websocket.WebSocket()
        self._ws.connect(url)

    def _setCurrentScene(self, scene_name):
        req = {"request-type": "SetCurrentScene", "message-id": "12345678", "scene-name": scene_name}
        self._request(req)
        # workaround fuer bug in obs-websocket
        self._reconnectToObs()

    def _setVisiblity(self, name, visibility):
        prop = self._getProperties(name)
        prop['visible'] = visibility
        self._setProperties(prop)

    def showUpcomingmatchScene(self, visibilitiy):
        for prop in self._upcomingSceneProp:
            prop['visible'] = visibilitiy
            self._setProperties(prop)

    def countdown(self, duration):
        interval_time = 0.1
        for ii in range(int(duration/interval_time)):
            countdown_time = duration-(ii*interval_time)
            s, subs = divmod(countdown_time, 1)
            text = '{:02.0f}:{:01.0f}'.format(s, subs*10)
            self._countdown_settings['text'] = text
            self._setSettings('countdown_txt_up', self._countdown_settings)
            time.sleep(interval_time)

    def setPros(self, pros, db):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        public_dir = os.path.join(script_dir, '../../public')
        self._pros = []
        numOfTeamMaxChars = 12
        for player in pros:
            db_pro = db.getPro(player['pro']['proId'])

            champion = db.getChampionName(player['championId'])
            champion = champion.replace('\'', '')
            champion = champion.replace(' ', '')
            champion = champion.replace('.', '')
            champ_path = self._toObsPath(os.path.join(script_dir, 'obs/champion/champion_small', champion +'.png'))
            ppic_path = self._toObsPath(os.path.join(public_dir, 'image/pros/medium', db_pro['image']['full']))
            perk1_path = self._toObsPath(os.path.join(script_dir, 'obs/perks_small', str(player['perks']['perkStyle'])+'.png'))
            perk2_path = self._toObsPath(os.path.join(script_dir, 'obs/perks_small', str(player['perks']['perkSubStyle'])+'.png'))
            
            if db_pro['teamId'] == 0:
                team = None
            else:
                team = db.getTeamName(db_pro['teamId'])
                team = (team[:(numOfTeamMaxChars-1)] + '..') if len(team) >= numOfTeamMaxChars else team
            
            pro = {'pic':ppic_path,
                   'name':player['pro']['nickName'],
                   'matchTeamId':player['teamId'],
                   'team':team,
                   'champion':champ_path,
                   'perk1':perk1_path,
                   'perk2':perk2_path}
            self._pros.append(pro)


        
    def startDiashow(self, interval_s):
        if ( len(self._pros) == 1 ):
            self._setupScene(self._pros[0])
            self._interval = None
        else:
            self._pro_index = len(self._pros) - 1
            self._interval = Interval(interval_s, self._intervalDiashow)
            self._interval.start()
            self._intervalDiashow()

    def stopDiashow(self):
        if self._interval:
            self._interval.stop()

    def _intervalDiashow(self):
        self._setupScene(self._pros[self._pro_index])
        if self._pro_index == 0:
            self._pro_index = len(self._pros) - 1
        else:
            self._pro_index = self._pro_index - 1

    def _request(self, request):
        self._ws.send(json.dumps(request))
        response = json.loads(self._ws.recv())
        return response

    def _getSettings(self, soureName):
        req = {"request-type": "GetSourceSettings", "message-id": "12345678", "sourceName": soureName}
        return self._request(req)['sourceSettings']

    def _setSettings(self, sourceName, settings):
        req = {"request-type": "SetSourceSettings", "message-id": "12345678", "sourceName": sourceName, 'sourceSettings':settings}
        return self._request(req)

    def _setMute(self, sourceName, mute):
        req = {"request-type": "SetSourceSettings", "message-id": "12345678", "source": sourceName, 'mute': mute}
        return self._request(req)

    def _getProperties(self, sourceName):
        req = {"request-type": "GetSceneItemProperties", "message-id": "12345678", "item": sourceName}
        return self._request(req)

    def _setProperties(self, properties):
        req = {"request-type": "SetSceneItemProperties", "item": properties['name']}
        req.update(properties)
        self._request(req)

    def startStreaming(self):
        req = {"request-type": "StartStreaming", "message-id": "12345678"}
        self._request(req)

    def stopStreaming(self):
        req = {"request-type": "StopStreaming", "message-id": "12345678"}
        self._request(req)

    def terminate(self):
        self._sys.terminate(self.obs_exe)
