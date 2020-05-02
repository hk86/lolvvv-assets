# this is the refactoring class to ../streamer/LoL.py

from datetime import datetime, timedelta
from glob import glob
from os import path, getcwd, remove, rename
from shutil import copyfile
from subprocess import Popen
from time import sleep
from tempfile import gettempdir
from zipfile import ZipFile

from win32api import GetFileVersionInfo, LOWORD, HIWORD # pip install pypiwin32

from PIL import Image
from pyautogui import locateCenterOnScreen, screenshot  # pip install pyautogui

from DirectInput import DirectKey, toggle_key, press_key, release_key
from Interval import Interval
from ingame_position import IngamePosition
from summoner.fact_team import FactTeamId
from tools import filename_time_string


class LoLState:
    UNKNOWN = 0
    NOT_RUNNING = 3
    FINISHED = 4
    RUNNING = 5


class LoLTimeSpeed:
    TIMESPEED_X1 = 0
    TIMESPEED_X2 = 1
    TIMESPEED_X4 = 2
    TIMESPEED_X8 = 3


class LoLDriver:
    _EXEC_TRIES = 3
    UPDATE_PLATFORM = 'EUW1'

    _FOCUS_KEYS = {
        FactTeamId.BLUE: [
            DirectKey.NUMERAL_1
            , DirectKey.NUMERAL_2
            , DirectKey.NUMERAL_3
            , DirectKey.NUMERAL_4
            , DirectKey.NUMERAL_5
        ],
        FactTeamId.RED: [
            DirectKey.q
            , DirectKey.w
            , DirectKey.e
            , DirectKey.r
            , DirectKey.t
        ]
    }

    def __init__(self, lol_path=r'C:\Riot Games\League of Legends'):
        self._game_folder = path.join(lol_path, 'Game')
        try:
            info = GetFileVersionInfo(path.join(self._game_folder, 'League of Legends.exe'), "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            last_release = HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
        except:
            last_release = 0, 0, 0, 0
        self._version = '.'.join(str(e) for e in last_release)
        self._lol_path = lol_path
        for image in self._get_saved_screenshots():
            remove(image)

    def _get_saved_screenshots(self):
        return glob(path.join(self._lol_path, 'Screenshots', '*.png'))

    def setup_settings(self, settings_path: str):
        persistant_settings = path.join(self._lol_path, 'Config',
                                        'PersistedSettings.json')
        copyfile(settings_path, persistant_settings)

    def restore_config(self, config_zip_path: str):
        lol_config = path.join(self._lol_path, 'Config')
        with ZipFile(config_zip_path, 'r') as config_zip:
            config_zip.extractall(Path=lol_config)

    def start_spectate(self, url: str, game_id: int, platform_id: str, encryption_key: str):
        cmd = [path.join(getcwd(), 'spectate.bat'),
               url,
               str(game_id),
               encryption_key,
               platform_id]
        self._exec_os_cmd(cmd, self._game_folder)

    def stop_lol(self):
        self._exec_os_cmd('taskkill /F /IM "League of Legends.exe"')

    def _exec_os_cmd(self, cmd, cwd=None):
        for tries in range(0, self._EXEC_TRIES):
            try:
                Popen(cmd, cwd=cwd)
                break
            except OSError:
                pass

    @staticmethod
    def toggle_pause_play():
        toggle_key(DirectKey.p)

    @staticmethod
    def toggle_scoreboard():
        toggle_key(DirectKey.o)

    @staticmethod
    def toggle_scoreboard_items():
        toggle_key(DirectKey.x)

    @staticmethod
    def toggle_timeline():
        toggle_key(DirectKey.u)

    @staticmethod
    def toggle_time_jump_back():
        toggle_key(DirectKey.BACK)
        sleep(1)

    @staticmethod
    def toggle_battle_mode():
        toggle_key(DirectKey.a)

    def toggle_player(self, match_team: FactTeamId, player_idx: int):
        key = self._FOCUS_KEYS[match_team][player_idx]
        toggle_key(key)

    @staticmethod
    def center_player():
        press_key(DirectKey.SPACE)

    @staticmethod
    def autocam():
        release_key(DirectKey.SPACE)
        toggle_key(DirectKey.d)

    @staticmethod
    def set_time_speed(speed: LoLTimeSpeed):
        toggle_key(DirectKey.NUM_0)
        for x in range(0, speed):
            toggle_key(DirectKey.NUM_PLUS)
            sleep(0.1)

    @property
    def state(self):
        screen = self.screenshot()
        if screen is None:
            return LoLState.NOT_RUNNING
        elif ((locateCenterOnScreen('images/Continue.png'))
              or
              (locateCenterOnScreen('images/GameOver.png'))):
            return LoLState.FINISHED
        elif locateCenterOnScreen('images/running.png'):
            return LoLState.RUNNING
        else:
            return LoLState.UNKNOWN

    def start_update(self):
        update_cmd = path.join(self._lol_path, 'LeagueClient.exe')
        self._exec_os_cmd(update_cmd, self._lol_path)

    def stop_update(self):
        self._exec_os_cmd('taskkill /F /IM "LeagueClientUx.exe"')

    def screenshot(self, title=None):
        toggle_key(DirectKey.F12)
        sleep(3)  # wait for screenshot has been saved to the file system
        images = self._get_saved_screenshots()
        if len(images) == 0:
            return
        last_img = images[-1]
        if title is None:
            screenshot_path = path.join(gettempdir(), filename_time_string() + ".png")
        else:
            screenshot_path = title + filename_time_string() + '.png'
        rename(last_img, screenshot_path)
        return Image.open(screenshot_path)

    @property
    def version(self):
        return self._version


class LeagueOfLegends(LoLDriver):
    _APPRECIATED_UPDATE_TIME_S = 300
    _APPRECIATED_REPAIR_TIME_S = 180
    _APPRECIATED_START_TIME_S = 35
    _SERVER_FOLLOWUP_TIME_S = 15
    _REPLAY_DATA_LOAD_TIME_S = 5
    _SECURE_TIMEOUT = 5
    _CONFIG_ZIP_PATH = r'../json/Config.zip'

    def __init__(self, lol_path='C:\\Riot Games\\League of Legends'):
        super().__init__(lol_path)
        self.restore_config(self._CONFIG_ZIP_PATH)
        self._in_game_pos = IngamePosition()
        self._focus_team = None
        self._focus_player_idx = -1
        self._show_items_duration_s = -1
        self._show_items_interval = None
        self._focus_interval = None

    def wait_for_spectate_start(self):
        sleep(self._APPRECIATED_START_TIME_S)
        sleep(self._SECURE_TIMEOUT)

    def wait_for_replay_start(self):
        self.wait_for_spectate_start()
        sleep(self._SERVER_FOLLOWUP_TIME_S)
        sleep(self._REPLAY_DATA_LOAD_TIME_S)

    def wait_for_update(self):
        sleep(self._APPRECIATED_UPDATE_TIME_S)

    def wait_for_repair(self):
        sleep(self._APPRECIATED_REPAIR_TIME_S)

    def stop_pending(self, timeout_s, check_interval_s):
        if check_interval_s > 4:
            check_interval_s = check_interval_s - 4  # time for locate on screen
        stop_time = (datetime.now() +
                     timedelta(seconds=timeout_s))
        while datetime.now() < stop_time:
            state = self.state
            if state == LoLState.UNKNOWN:
                sleep(check_interval_s)
            else:
                break
        if state == LoLState.UNKNOWN:
            screenshot('noExit' + filename_time_string() + '.png')
            state = LoLState.FINISHED
        self.stop_lol()
        return state

    def modify_ui(self):
        self.toggle_scoreboard()
        self.toggle_timeline()

    def start_toggle_items(self, interval_s, duration_s):
        self._show_items_duration_s = duration_s
        self._show_items_interval = Interval(interval_s, self._show_items)
        self._show_items_interval.start()

    def stop_toggle_items(self):
        self._show_items_interval.stop()

    def focus_player(self, team_id: int, in_team_idx: int):
        self._focus_team = team_id
        self._focus_player_idx = in_team_idx
        toggle_interval_s = 1
        self._focus_player()
        self.center_player()
        self._focus_interval = Interval(toggle_interval_s,
                                        self._focus_player)
        self._focus_interval.start()

    def unfocus_player(self):
        if not self._focus_interval:
            return
        self._focus_interval.stop()
        self.autocam()

    def _focus_player(self):
        self.toggle_player(self._focus_team, self._focus_player_idx)

    def specate_timeshift(self, time: timedelta):
        time_s = time.total_seconds()
        print('specate_timeshift for {} seconds'.format(time_s))
        if time_s < 0:
            count_back_jumps = int(time_s / (-15))
            # 15 seconds per jump
            time = count_back_jumps * timedelta(seconds=-15)
            for x in range(0, count_back_jumps):
                self.toggle_time_jump_back()
        else:
            fast_forward_time_s = time_s / 8
            self.set_time_speed(LoLTimeSpeed.TIMESPEED_X8)
            sleep(fast_forward_time_s)
            self.set_time_speed(LoLTimeSpeed.TIMESPEED_X1)
        return time

    def _show_items(self):
        self.toggle_scoreboard_items()
        sleep(self._show_items_duration_s)
        self.toggle_scoreboard_items()

    def cleanup_event_list(self):
        self.toggle_battle_mode()
        self.toggle_battle_mode()

    def init_positions(self):
        """
        have to be called after ui is modified and 1 sec timeout
        :return:
        """
        self._in_game_pos.init_champs(self.screenshot())

    def focus_champ(self, champ_key: str, team_id: FactTeamId):
        in_game_champ = self._in_game_pos.get_in_game_champ(champ_key, team_id)
        if not in_game_champ:
            return
        self.focus_player(team_id, in_game_champ.in_team_idx)

    def __del__(self):
        try:
            self._focus_interval.stop()
        except AttributeError:
            pass
