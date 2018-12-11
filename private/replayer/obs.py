from subprocess import run, Popen
import collections
import json
import os
from time import sleep
import threading
from pathlib import Path
from shutil import copyfile

from Interval import Interval
from event import Event
from summoner.fact_perks import FactPerks
from summoner.static_pro import StaticPro
from summoner.fact_team import FactTeamId
from database.pro_team import ProTeam
from image_service import ImageService

import platform

# pip install websocket-client
import websocket
from pprint import pprint # for debug

class ObsDriver:
    _message_id = 1

    def __init__(self, obs_path):
        self._obs_path = obs_path

    def setup_scene(self, scene_path):
        scene_name = os.path.basename(scene_path)
        obs_scene = os.path.join(
            os.getenv('APPDATA'),
            'obs-studio/basic/scenes',
            scene_name)
        copyfile(scene_path, obs_scene)

    def obs_start(self):
        if platform.architecture()[0] == '64bit':
            arch='64bit'
            self._obs_exe='obs64.exe'
        else:
            arch='32bit'
            self._obs_exe='obs32.exe'
        _obs_path = os.path.join(self._obs_path, 'bin', arch)
        obs_full_path = os.path.join(_obs_path, self._obs_exe)
        Popen(
            [obs_full_path],
            cwd=_obs_path
            )

    def _reconnect_obs_ws(self, url='ws://localhost:4444'):
        self._ws=None
        self._ws=websocket.WebSocket()
        self._ws.connect(url)

    def _request(self, request):
        for tries in range(0, 5): #workaround for some issues in websocket communication
            self._message_id += 1
            request['message-id'] = str(self._message_id)
            self._ws.send(json.dumps(request))
            response = json.loads(self._ws.recv())
            if 'error' not in response:
                break
        return response

    def _getSettings(self, soureName):
        req = {"request-type": "GetSourceSettings", "sourceName": soureName}
        return self._request(req)['sourceSettings']

    def _setSettings(self, sourceName, settings):
        req = {"request-type": "SetSourceSettings", "sourceName": sourceName, 'sourceSettings':settings}
        return self._request(req)

    def _setMute(self, sourceName, mute):
        req = {"request-type": "SetSourceSettings", "source": sourceName, 'mute': mute}
        return self._request(req)

    def _getProperties(self, sourceName):
        req = {"request-type": "GetSceneItemProperties", "item": sourceName}
        for tries in range(0, 5): #workaround for some issues in websocket communication
            response = self._request(req)
            if 'bounds' in response:
                break
        return response

    def _setProperties(self, properties):
        req = {"request-type": "SetSceneItemProperties", "item": properties['name']}
        req.update(properties)
        self._request(req)

    def startStreaming(self):
        req = {"request-type": "StartStreaming"}
        self._request(req)

    def stopStreaming(self):
        req = {"request-type": "StopStreaming"}
        self._request(req)

    def start_recording(self):
        req = {"request-type": "StartRecording"}
        self._request(req)

    def stop_recording(self):
        req = {"request-type": "StopRecording"}
        self._request(req)

    def get_recording_folder(self):
        req = {"request-type": "GetRecordingFolder"}
        return self._request(req)['rec-folder']

    def set_recording_folder(self, path):
        req = {"request-type": "SetRecordingFolder",
               "rec-folder": os.path.abspath(path)}
        self._request(req)

    def terminate(self):
        run('taskkill /F /IM {}'.format(self._obs_exe))

    def _setCurrentScene(self, scene_name):
        req = {"request-type": "SetCurrentScene", "scene-name": scene_name}
        self._request(req)
        # workaround fuer bug in obs-websocket
        self._reconnect_obs_ws()

    def _setVisiblity(self, name, visibility):
        prop = {"visible": visibility, "name": name}
        self._setProperties(prop)

class Obs(ObsDriver):
    _SCENE_PATH = r''
   
    def __init__(self, obs_path):
        super().__init__(obs_path)
        self.setup_scene(self._SCENE_PATH)
        self.obs_start()
        OBS_LOAD_TIME_S = 5
        sleep(OBS_LOAD_TIME_S)
        self._reconnect_obs_ws()

    def _set_img_file(self, name, file_path):
        settings = {"file": self._toObsPath(file_path)}
        return self._setSettings(name, settings)

    def _set_txt(self, name, text:str):
        settings = {"text": text}
        self._setSettings(name, settings)

    def _set_txt_color(self, name:str, color:int):
        settings = {"color": color}
        self._setSettings(name, settings)

    def _toObsPath(self, path):
        return Path(os.path.abspath(path)).as_posix()

class ObsClips(Obs):
    _SCENE_PATH = r'../json/lolvvv_1080p_clips.json'
    _MAX_CHARS_PROTEAM_TXT = 17
    _BLUE_COLOR = 13665569
    _RED_COLOR = 2631899

    def __init__(self, obs_path=r'C:\Program Files\obs-studio'):
        super().__init__(obs_path)
        self._images = ImageService()
        backgrounds = ['banner_event_png', 'banner_runes1_png',
            'banner_runes2_png', 'banner_proplayer_png']
        for name in backgrounds:
            self._set_img_file(name,
            self._images.background_img_path())
        banners = ['banner_left', 'banner_middle']
        for name in banners:
            self._set_img_file(name, self._images.banner_img_path())
        logos = ['lolvvv_logo', 'lolvvv_png']
        for lolvvv_logo in logos:
            self._set_img_file(lolvvv_logo,
                self._images.logo_img_path()
            )
        self._set_img_file('overview_wallpaper_png', 
            self._images.wallpaper_img_path()
        )
        self._set_img_file('twitch_logo', 
            self._images.twitch_img_path()
        )

    def show_pregame_overlay(self, visibilitiy):
        self._setVisiblity('pregame_overlay', visibilitiy)
        self._setVisiblity('ingame_clips', not visibilitiy)

    def set_champion(self, champion_key):
        self._set_img_file('championplayed_img', 
            self._images.champ_small_img_path(champion_key)
        )
        self._set_img_file('champion_png', 
            self._images.champbanner_img_path(champion_key)
        )

    def _set_perk(self, name, perk_id:int):
        self._set_img_file(name, self._images.perk_img_path(perk_id))

    def set_perks(self, perks:FactPerks):
        self._set_perk('rune1.0_png', perks.rune1_0)
        self._set_perk('rune1.1_png', perks.rune1_1)
        self._set_perk('rune1.2_png', perks.rune1_2)
        self._set_perk('rune1.3_png', perks.rune1_3)
        self._set_perk('rune1.4_png', perks.rune1_4)
        self._set_perk('rune2.0_png', perks.rune2_0)
        self._set_perk('rune2.1_png', perks.rune2_1)
        self._set_perk('rune2.2_png', perks.rune2_2)
        self._set_img_file('perks1_img',
            self._images.perk_small_img_path(perks.rune1_0)
        )
        self._set_img_file('perks2_img',
            self._images.perk_small_img_path(perks.rune2_0)
        )

    def set_main_pro(self, main_pro: StaticPro):
        nickname = main_pro.nickname
        self._set_txt('proplayername_txt', nickname)
        self._set_txt('proplayer_txt', nickname)
        self._set_img_file('proplayer_img',
            self._images.pro_med_img_path(main_pro.image)
        )

    def set_fact_team(self, fact_team_id: FactTeamId):
        # set teamcolour_img ?
        color_code = 0
        if fact_team_id == FactTeamId.BLUE:
            color_code = self._BLUE_COLOR
        else:
            color_code = self._RED_COLOR
        self._set_txt_color('proplayername_txt', color_code)
        self._set_txt_color('proteam_txt', color_code)

    def set_pro_team(self, pro_team: ProTeam):
        if pro_team:
            fitted_name = pro_team.name
            if len(fitted_name) >= self._MAX_CHARS_PROTEAM_TXT:
                fitted_name = (fitted_name
                    [:self._MAX_CHARS_PROTEAM_TXT-1] + '..')
            self._set_txt('proteam_txt', fitted_name)
            self._set_txt('team_txt', fitted_name)
            self._set_img_file('team_logo_png',
                self._images.team_med_img_path(pro_team.image))
            visibility = True
        else:
            visibility = False
        team_elements = ['proteam_txt', 'team_txt', 'team_logo_png']
        for element in team_elements:
            self._setVisiblity(element, visibility)

    def set_event(self, event: Event):
        self._set_txt('event_txt', event.ev_type)

class ObsStreamer(Obs):
    _SCENE_PATH = r'../json/obs_lolvvv_1080p.json'

    def __init__(self, obs_path=r'C:\Program Files\obs-studio'):
        super().__init__(obs_path)
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

    def showUpcomingmatchScene(self, visibilitiy):
        for prop in self._upcomingSceneProp:
            self._setVisiblity(prop['name'], visibilitiy)

    def countdown(self, duration):
        interval_time = 0.1
        for ii in range(int(duration/interval_time)):
            countdown_time = duration-(ii*interval_time)
            s, subs = divmod(countdown_time, 1)
            text = '{:02.0f}:{:01.0f}'.format(s, subs*10)
            self._countdown_settings['text'] = text
            self._setSettings('countdown_txt_up', self._countdown_settings)
            sleep(interval_time)

    def setPros(self, pros, db):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        public_dir = os.path.join(script_dir, '../../public')
        self._pros = []
        numOfTeamMaxChars = 17
        for player in pros:
            db_pro = db.getPro(player['pro']['proId'])

            champion = db.getChampionKey(player['championId'])
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




