from database.meteor import Meteor
from database.static_pro_db import StaticProDb
from database.static_champ_db import StaticChampDb
from database.pro_team_db import ProTeamDb
from summoner.fact_perks import FactPerks
from summoner.ingame_pro import IngamePro
from match.spectate_match import SpectateMatch
from event import Event
from clip import Clip
from video import Video
from obs import ObsClips
from LoL import LeagueOfLegends, LoLState

from os import path
from pathlib import Path
from datetime import timedelta, datetime
from time import sleep
from glob import glob


class ClipRecorder:
    _MAIN_VIDEO_FOLDER = r'./replays/clips'
    _RECORDING_OVERTIME_S = 15
    _PREGAME_TIME_S = 3
    _RELEASE_HANDLE_TIME_S = 3

    def __init__(self, meteor_db: Meteor, lol: LeagueOfLegends):
        self._static_pro_db = StaticProDb(meteor_db)
        self._static_champ_db = StaticChampDb(meteor_db)
        self._pro_team_db = ProTeamDb(meteor_db)
        self._obs = ObsClips()
        self._lol = lol

    def prepare_clips(self, events: [Event]):
        clips = []
        ingame_clip_num = 0
        for event in events:
            main_pros = self._summoners_to_pros([event.main_summoner])
            if len(main_pros) == 0:
                continue
            ingame_clip_num += 1
            clip = Clip()
            clip.ingame_clip_num = ingame_clip_num
            clip.event = event
            clip.main_pros = main_pros
            clip.participant_pros = self._summoners_to_pros(
                event.participants)
            clip.victim_pros = self._summoners_to_pros(
                event.victims)
            clips.append(clip)
        return clips

    def _get_clip_video_path(self, clip):
        match_path = path.join(
            self._MAIN_VIDEO_FOLDER,
            clip.event.platform_id,
            str(clip.event.game_id)
        )
        return path.join(match_path, str(clip.ingame_clip_num))

    def record_clips(self, clips: [Clip], match: SpectateMatch):
        if self._try_start_lol(match) != LoLState.RUNNING:
            return []
        self._init_lol_match()
        ingame_time = timedelta(seconds=0)
        lol = self._lol
        match_video_path = self._MAIN_VIDEO_FOLDER
        for clip in clips:
            timeshift = clip.event.start_time - ingame_time \
                        - timedelta(seconds=20)
            ingame_time += lol.specate_timeshift(timeshift)
            lol.toggle_pause_play()
            clip_folder = path.join(match_video_path,
                                    str(clip.ingame_clip_num))
            Path(clip_folder).mkdir(parents=True, exist_ok=True)
            self._obs.set_recording_folder(clip_folder)
            self._obs.show_pregame_overlay(True)
            killer_summoner = clip.event.main_summoner
            self._obs.set_perks(FactPerks(killer_summoner.fact_stats))
            main_champ = self._static_champ_db\
                                   .get_champ_key(killer_summoner.champ_id)
            self._obs.set_champion(main_champ)
            self._obs.set_main_pro(clip.main_pros[0])
            pro_team = self._pro_team_db.get_pro_team(
                clip.main_pros[0].team_id)
            self._obs.set_pro_team(pro_team)
            self._obs.set_fact_team(killer_summoner.team)
            self._obs.set_event(clip.event)
            lol.cleanup_event_list()
            lol.modify_ui()
            self._obs.start_recording()
            sleep(self._PREGAME_TIME_S)
            if clip.event.main_focus:
                lol.focus_champ(main_champ, killer_summoner.team)
            self._obs.show_pregame_overlay(False)
            lol.toggle_pause_play()
            start_record = datetime.now()
            sleep(clip.event.length.total_seconds()
                  + self._RECORDING_OVERTIME_S
                  + clip.event.event_based_rec_overtime_s)
            self._obs.stop_recording()
            lol.unfocus_player()
            sleep(self._RELEASE_HANDLE_TIME_S)
            clip_length = (datetime.now() - start_record)
            ingame_time += clip_length
            clip.video = Video(glob(path.join(clip_folder, '*.*'))[0])
        lol.stop_lol()
        return clips

    def _try_start_lol(self, match: SpectateMatch):
        start_tries = 3
        lol = self._lol
        state = LoLState.UNKNOWN
        for x in range(0, start_tries):
            print('url: {}'.format(match.url))
            print('game: {} plat: {}'.format(match.game_id, match.platform_id))
            print('enc: {}'.format(match.encryption_key))
            lol.start_spectate(
                match.url,
                match.game_id,
                match.platform_id,
                match.encryption_key
            )
            lol.wait_for_replay_start()
            state = lol.state
            print('lol state {}'.format(state))
            if state == LoLState.RUNNING:
                break
            lol.screenshot('notStarted')
            lol.stop_lol()
            # try to repair lol
            if state == LoLState.UNKNOWN:
                lol.start_update()
                lol.wait_for_repair()
                lol.stop_update()
        return state

    def _init_lol_match(self):
        self._lol.modify_ui()
        sleep(2)
        self._lol.init_positions()
        self._lol.specate_timeshift(timedelta(minutes=-1))

    def _timeshift_to_clip(self, ingame_time, clip_event):
        timeshift = clip_event.event.start_time - ingame_time \
                    - timedelta(seconds=20)
        shift_time = self._lol.specate_timeshift(timeshift)
        self._lol.toggle_pause_play()
        return shift_time

    def _prepare_for_record(self, clip):
        clip_folder = self._get_clip_video_path(clip)
        Path(clip_folder).mkdir(parents=True, exist_ok=True)
        self._obs.set_recording_folder(clip_folder)
        self._obs.show_pregame_overlay(True)
        killer_summoner = clip.event.main_summoner
        self._obs.set_perks(FactPerks(killer_summoner.fact_stats))
        main_champ = self._static_champ_db \
            .get_champ_key(killer_summoner.champ_id)
        self._obs.set_champion(main_champ)
        self._obs.set_main_pro(clip.main_pros[0])
        pro_team = self._pro_team_db.get_pro_team(
            clip.main_pros[0].team_id)
        self._obs.set_pro_team(pro_team)
        self._obs.set_fact_team(killer_summoner.team)
        self._obs.set_event(clip.event)
        self._lol.cleanup_event_list()
        self._lol.modify_ui()
        if clip.event.main_focus:
            self._lol.focus_champ(main_champ, killer_summoner.team)

    def _summoners_to_pros(self, summoners):
        pros = []
        for summoner in summoners:
            pro = self._static_pro_db.get_static_pro(
                summoner.account_id,
                summoner.platform_id
            )
            if pro:
                pros.append(IngamePro(pro, summoner))
        return pros
