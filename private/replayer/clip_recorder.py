from database.meteor import Meteor
from database.static_pro_db import StaticProDb
from database.static_champ_db import StaticChampDb
from database.pro_team_db import ProTeamDb
from summoner.fact_perks import FactPerks
from match.spectate_match import SpectateMatch
from event import Event
from clip import Clip
from obs import ObsClips
from kill_row import KillRow
from LoL import LeagueOfLegends, LoLState

from os import path
from pathlib import Path
from datetime import timedelta, datetime
from time import sleep
from glob import glob

class ClipRecorder:
    _MAIN_VIDEO_FOLDER = r'./replays/clips'
    _RECORDING_OVERTIME_S = 25
    _PREGAME_TIME_S = 5

    def __init__(self, meteor_db: Meteor, lol: LeagueOfLegends):
        self._static_pro_db = StaticProDb(meteor_db)
        self._static_champ_db = StaticChampDb(meteor_db)
        self._pro_team_db = ProTeamDb(meteor_db)
        self._obs = ObsClips()
        self._lol = lol

    def record_clips(self, events:[Event], match:SpectateMatch):
        clips = []
        for event in events:
            main_pro = self._summoners_to_pros([event.main_summoner])
            if len(main_pro) > 0:
                clip = Clip()
                clip.event = event
                clip.main_pro = main_pro[0]
                clip.participant_pros = self._summoners_to_pros(
                    event.participants
                )
                clip.victim_pros = self._summoners_to_pros(
                    event.victims
                )
                clips.append(clip)
        if len(clips) > 0:
            match_video_path = path.join(
                self._MAIN_VIDEO_FOLDER,
                clips[0].event.platform_id,
                str(clips[0].event.game_id)
            )
            START_TRIES = 3
            lol = self._lol
            for x in range(0, START_TRIES):
                lol.start_spectate(
                    match.url,
                    match.game_id,
                    match.platform_id,
                    match.encryption_key
                )
                lol.wait_for_replay_start()
                if (lol.check_running() == LoLState.UNKNOWN):
                    break
                lol.stop_lol()
                if (x == START_TRIES-1):
                    # ToDo: was soll hier geschehen?
                    pass
            lol.modify_ui()
            lol.specate_timeshift(timedelta(minutes=-1))
            ingame_time = timedelta(seconds=0)
            clip_counter = 0
            for clip in clips:
                clip_counter += 1
                timeshift = event.start_time - ingame_time
                ingame_time += lol.specate_timeshift(timeshift)
                ingame_time += lol.specate_timeshift(timedelta(seconds=-15))
                clip_folder = path.join(match_video_path,
                                str(clip_counter))
                Path(clip_folder).mkdir(parents=True, exist_ok=True)
                self._obs.set_recording_folder(clip_folder)
                self._obs.show_pregame_overlay(True)
                killer_summoner = clip.event.main_summoner
                killer_stats = (killer_summoner.get_fact_stats())
                self._obs.set_perks(FactPerks(killer_stats))
                self._obs.set_champion(self._static_champ_db
                    .get_champ_key(
                        killer_summoner.get_champ_id()))
                self._obs.set_main_pro(clip.main_pro)
                pro_team = self._pro_team_db.get_pro_team(
                    clip.main_pro.team_id)
                self._obs.set_pro_team(pro_team)
                self._obs.set_fact_team(killer_summoner.team)
                self._obs.set_event(clip.event)
                self._obs.start_recording()
                start_record = datetime.now()
                sleep(self._PREGAME_TIME_S)
                lol.focus_player(
                    killer_summoner.team,
                    killer_summoner.get_inteam_idx)
                self._obs.show_pregame_overlay(False)
                sleep(clip.event.length + self._RECORDING_OVERTIME_S - self._PREGAME_TIME_S)
                self._obs.stop_recording()
                ingame_time += (datetime.now() - start_record)
                clip.clip_path = glob(path.join(clip_folder, '*.*'))[0]
            lol.stop()
        return clips


    def _summoners_to_pros(self, summoners):
        pros = []
        for summoner in summoners:
            pro = self._static_pro_db(
                summoner.account_id,
                summoner.platform_id
            )
            if pro:
                pros.append(pro)
        return pros
    

    