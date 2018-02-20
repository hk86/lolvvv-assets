import websocket
import subprocess
import collections
import json
import os
import time
import threading
from pathlib import Path

from Interval import *

import platform

# for debug
import pprint

class OBS():
   
    def __init__(self, obs_path='C:\\Program Files (x86)\\obs-studio'):
        if platform.architecture()[0] == '64bit':
            arch='64bit'
            self.obs_exe='obs64.exe'
        else:
            arch='32bit'
            self.obs_exe='obs32.exe'

        _obs_path = os.path.join(obs_path, 'bin', arch)
        subprocess.Popen([os.path.join(_obs_path, self.obs_exe)], cwd=_obs_path)
        time.sleep(3) # wait for obs launching

        self._ws=websocket.WebSocket()
        self._ws.connect('ws://localhost:4444')

        self._proTeam_props = self._getProperties('proteam_diashow')
        self._pros_settings = self._getSettings('pros_diashow')
        self._proName_settings = self._getSettings('proname_diashow')
        self._proTeam_settings = self._getSettings('proteam_diashow')
        self._champion_settings = self._getSettings('champion_diashow')
        self._perk1_settings = self._getSettings('perks1_diashow')
        self._perk2_settings = self._getSettings('perks2_diashow')
    
    def _toObsPath(self, path):
        return Path(os.path.abspath(path)).as_posix()

    def _setupScene(self, pro):
        self._pros_settings['file'] = pro['pic']
        self._proName_settings['text'] = pro['name']
        self._champion_settings['file']=pro['champion']
        self._perk1_settings['file']=pro['perk1']
        self._perk2_settings['file']=pro['perk2']

        self._setSettings('pros_diashow', self._pros_settings)
        self._setSettings('proname_diashow', self._proName_settings)
        self._setSettings('champion_diashow', self._champion_settings)
        self._setSettings('perks1_diashow', self._perk1_settings)
        self._setSettings('perks2_diashow', self._perk2_settings)

        if pro['team']:
            self._proTeam_settings['text'] = pro['team']
            self._setSettings('proteam_diashow', self._proTeam_settings)
            self._proTeam_props['visible'] = True
            self._setProperties('proteam_diashow', self._proTeam_props)
        else:
            self._proTeam_props['visible'] = False
            self._setProperties('proteam_diashow', self._proTeam_props)



    def setPros(self, pros, db):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        public_dir = os.path.join(script_dir, '../../public')
        self._pros = []
        for player in pros:
            db_pro = db.getPro(player['pro']['proId'])

            champion = db.getChampionName(player['championId'])
            champion.replace('\'', '')
            champion.replace(' ', '')
            champion.replace('.', '')
            champ_path = self._toObsPath(os.path.join(script_dir, 'obs/champion', champion +'.png'))
            ppic_path = self._toObsPath(os.path.join(public_dir, 'image/pros/medium', db_pro['image']['full']))
            perk1_path = self._toObsPath(os.path.join(public_dir, 'perks', str(player['perks']['perkStyle'])+'.png'))
            perk2_path = self._toObsPath(os.path.join(public_dir, 'perks', str(player['perks']['perkSubStyle'])+'.png'))
            
            if db_pro['teamId'] == 0:
                team = None
            else:
                team = db.getTeamName(db_pro['teamId'])
            
            pro = {'pic':ppic_path,
                   'name':player['pro']['nickName'],
                   'team':team,
                   'champion':champ_path,
                   'perk1':perk1_path,
                   'perk2':perk2_path}
            self._pros.append(pro)


        
    def startDiashow(self, interval_s):
        if ( len(self._pros) == 1 ):
            self._setupScene(self._pros[0])
            self._interval = None
            print('thread will not starting')
        else:
            self._pro_index = len(self._pros) - 1
            self._interval = Interval(interval_s, self._intervalDiashow)
            self._interval.start()
            self._intervalDiashow()

    def stopDiashow(self):
        if self._interval:
            self._interval.stop()

    def _intervalDiashow(self):
        print('thread')
        #pprint.pprint(threading.Timer(5, self._intervalDiashow).start())
        self._setupScene(self._pros[self._pro_index])
        if self._pro_index == 0:
            self._pro_index = len(self._pros) - 1
        else:
            self._pro_index = self._pro_index - 1

    def _request(self, request):
        self._ws.send(json.dumps(request))
        return json.loads(self._ws.recv())

    def _getSettings(self, soureName):
        req = {"request-type": "GetSourceSettings", "message-id": "12345678", "sourceName": soureName}
        return self._request(req)['sourceSettings']

    def _setSettings(self, sourceName, settings):
        req = {"request-type": "SetSourceSettings", "message-id": "12345678", "sourceName": sourceName, 'sourceSettings':settings}
        return self._request(req)

    def _getProperties(self, sourceName):
        req = {"request-type": "GetSceneItemProperties", "message-id": "12345678", "item": sourceName}
        return self._request(req)

    def _setProperties(self, sourceName, properties):
        req = {"request-type": "SetSceneItemProperties", "item": sourceName}
        req.update(properties)
        self._ws.send(json.dumps(req))

    def test(self):
        print('test')
        self._proTeam_props['visible'] = False
        self._setProperties('proteam_diashow', self._proTeam_props)

    def start(self):
        req = {"request-type": "StartStreaming", "message-id": "12345678"}
        self._request(req)

    def stop(self):
        req = {"request-type": "StopStreaming", "message-id": "12345678"}
        self._request(req)

    def terminate(self):
        subprocess.call(['kill.bat', self.obs_exe])
