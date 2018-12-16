#this is the refactoring class to ../streamer/LoL.py

from os import path, walk, getcwd
from subprocess import run
from datetime import datetime, timedelta
from time import sleep
from array import array

from DirectInput import DirectKey, toggle_key, press_key, release_key
from Interval import Interval
from summoner.fact_team import FactTeamId

from pyautogui import locateCenterOnScreen, screenshot #pip install pyautogui

class LoLState:
    UNKNOWN = 0
    PENDING = 1
    CRASHED = 2
    DATA_UNAVAILBLE = 3
    FINISHED = 4
    RUNNING = 5

class LoLTimeSpeed:
    TIMESPEED_X1 = 0
    TIMESPEED_X2 = 1
    TIMESPEED_X4 = 2
    TIMESPEED_X8 = 3

class LoLDriver:
    UPDATE_PLATFORM = 'EUW1'

    _BLUE_FOCUS_KEYS = array('B', [
        DirectKey.NUMERAL_1
        , DirectKey.NUMERAL_2
        , DirectKey.NUMERAL_3
        , DirectKey.NUMERAL_4
        , DirectKey.NUMERAL_5
    ])
    
    _RED_FOCUS_KEYS = array('B', [
        DirectKey.q
        , DirectKey.w
        , DirectKey.e
        , DirectKey.r
        , DirectKey.t
    ])

    def __init__(self, lol_path=r'C:\Riot Games\League of Legends'):
        releases_path = path.join(lol_path, 'RADS','solutions',
                              'lol_game_client_sln','releases')
        installed_releases = next(walk(releases_path))[1]
        installed_releases.sort(reverse=True)
        self._lol_path = lol_path
        self._version = installed_releases[0]
        self._deploy_path = path.join(releases_path, self._version, 'deploy')

    def start_spectate(self, url:str, game_id:int, platform_id:str, encryption_key:str):
        cmd = [path.join(getcwd(), 'spectate.bat'),
               url,
               str(game_id),
               encryption_key,
               platform_id]
        run(cmd, cwd=self._deploy_path)

    def stop_lol(self):
        run('taskkill /F /IM "League of Legends.exe"')

    def toggle_scoreboard(self):
        toggle_key(DirectKey.o)

    def toggle_scoreboard_items(self):
        toggle_key(DirectKey.x)

    def toggle_timeline(self):
        toggle_key(DirectKey.u)

    def toggle_time_jump_back(self):
        toggle_key(DirectKey.BACK)
        sleep(0.5)

    def toggle_player(self, match_team: FactTeamId, player_idx: int):
        if match_team == FactTeamId.BLUE:
            toggle_key(self._BLUE_FOCUS_KEYS[player_idx])
        else:
            toggle_key(self._RED_FOCUS_KEYS[player_idx])

    def center_player(self):
        press_key(DirectKey.SPACE)

    def autocam(self):
        release_key(DirectKey.SPACE)
        toggle_key(DirectKey.d)

    def set_time_speed(self, speed: LoLTimeSpeed):
        toggle_key(DirectKey.NUM_0)
        for x in range(0, speed):
            toggle_key(DirectKey.NUM_PLUS)
            sleep(0.1)
        
    def state(self):
        if (locateCenterOnScreen('images/PendingLoL.png')):
            return LoLState.PENDING
        elif (locateCenterOnScreen('images/lolCrashed.png')
            or
            (locateCenterOnScreen('images/bugsplat.png'))):
            return LoLState.CRASHED
        elif (locateCenterOnScreen('images/dataUnavailable.png')):
            return LoLState.DATA_UNAVAILBLE
        elif ((locateCenterOnScreen('images/Continue.png'))
              or
              (locateCenterOnScreen('images/GameOver.png'))):
            return LoLState.FINISHED
        elif ((locateCenterOnScreen('images/running.png'))):
            return LoLState.RUNNING
        else:
            return LoLState.UNKNOWN

    def start_update(self):
        update_cmd = path.join(self._lol_path, 'LeagueClient.exe')
        run(update_cmd, cwd=self._lol_path)

    def stop_update(self):
        run('taskkill /F /IM "LeagueClientUx.exe"')

    @property
    def version(self):
        return self._version


class LeagueOfLegends(LoLDriver):
    _APPRECIATED_UPDATE_TIME_S = 300
    _APPRECIATED_START_TIME_S = 35
    _SERVER_FOLLOWUP_TIME_S = 15
    _REPLAY_DATA_LOAD_TIME_S = 5
    _SECURE_TIMEOUT = 5

    def __init__(self, lol_path = 'C:\\Riot Games\\League of Legends'):
        super().__init__(lol_path)

    def _time_string(self): # should be in sw_tools or something like this.
        return datetime.now().strftime('%Y-%m-%d_%H%M%S')

    def wait_for_spectate_start(self):
        sleep(self._APPRECIATED_START_TIME_S)
        sleep(self._SECURE_TIMEOUT)

    def wait_for_replay_start(self):
        self.wait_for_spectate_start()
        sleep(self._SERVER_FOLLOWUP_TIME_S)
        sleep(self._REPLAY_DATA_LOAD_TIME_S)

    def wait_for_update(self):
        sleep(self._APPRECIATED_UPDATE_TIME_S)

    def check_running(self):
        state = self.state()
        if ((state == LoLState.PENDING) or
            (state == LoLState.CRASHED)):
            screenshot('notRunning' + self._time_string() + '.png')
        return state

    def stop_pending(self, timeout_s, check_interval_s):
        if (check_interval_s > 4):
            check_interval_s = check_interval_s - 4 #time for locate on screen
        stop_time = (datetime.now() +
                     timedelta(seconds=check_interval_s))
        while (datetime.now() < stop_time):
            state = self.state()
            if (state == LoLState.UNKNOWN):
                sleep(check_interval_s)
            else:
                break
        if (state == LoLState.UNKNOWN):
            screenshot('noExit' + self._time_string() + '.png')
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

    def focus_player(self, team_id: int, inteam_idx: int):
        self._focus_team = team_id
        self._focus_player_idx = team_id - 1
        TOGGLE_INTERVAL_S = 1
        self._focus_player()
        self.center_player()
        self._focus_interval = Interval(TOGGLE_INTERVAL_S,
                                        self._focus_interval)
        self._focus_interval.start()

    def unfocus_player(self):
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
            fast_forward_time_s = time_s/8
            self.set_time_speed(LoLTimeSpeed.TIMESPEED_X8)
            sleep(fast_forward_time_s)
            self.set_time_speed(LoLTimeSpeed.TIMESPEED_X1)
        return time

    def _show_items(self):
        self.toggle_scoreboard_items()
        sleep(self._show_items_duration_s)
        self.toggle_scoreboard_items()