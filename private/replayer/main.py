import logging
from datetime import datetime, timedelta
from os import path, system, listdir
from shutil import rmtree
from time import sleep

from LoL import LeagueOfLegends
from clip import Clip
from clip_recorder import ClipRecorder
from database.clip_store_service import ClipStoreService
from database.fact_db import FactDataDb
from database.meteor import Meteor
from database.static_pro_db import StaticProDb
from event import generate_events, EventTripleKill
from logger import Logger
from match.fact_match import FactMatch
from match.fact_replay import FactReplay
from match.match import Match
from match.replay import Replay
from match.spectate_match import SpectateMatch
from patch_version import PatchVersion
from replay_hoover import ReplayHoover
from replay_manager import ReplayManager
from s3_clip_upload import S3ClipUpload


class Clipper:
    _MIN_RUNTIME = timedelta(hours=8)
    _MAX_TIME_REPLAY_PENDING = timedelta(hours=8)
    MAX_MATCHES_PER_SCAN = 50
    _OBS_FILE_HANDLE_WAIT_TIME = 10

    def __init__(self, meteor_db: Meteor):
        self._logger = Logger('clipper', logging.DEBUG)
        self._logger.warning('start')
        self._start_time = datetime.now()
        self._fact_db = FactDataDb('mongodb://replayer:qdgr4nlXF6IOy@88.99.138.8:27017/meteor?authSource=admin')
        self._meteor_db = meteor_db
        self._clip_store = ClipStoreService(self._meteor_db)
        self._static_pro_db = StaticProDb(self._meteor_db)
        self._patch_version = PatchVersion(self._meteor_db)
        self._replay_manager = ReplayManager()
        self._lol = LeagueOfLegends()
        self._playable_patch = self._lol_patch()
        if not self._playable_patch:
            self.upgrade_lol()
        self._logger.warning('playable match: {}'.format(self._playable_patch))
        self._recorder = ClipRecorder(self._meteor_db, self._lol)
        self._store_service = S3ClipUpload()
        self._replay_hoover = ReplayHoover(self._meteor_db)

    def upgrade_lol(self):
        self._logger.warning('upgrade lol')
        self._lol.start_update()
        self._logger.warning('wait for upgrade')
        self._lol.wait_for_update()
        self._logger.warning('stop upgrade')
        self._lol.stop_update()
        self._logger.warning('delete lol object')
        del self._lol
        self._logger.warning('create new lol object')
        self._lol = LeagueOfLegends()
        self._logger.warning('get new lol patch version')
        self._playable_patch = self._lol_patch()
        self._logger.warning('check for new lol version')
        if not self._playable_patch:
            # if this lol version is currently not known in db, save the current lol version
            # related to the current server patch version
            self._logger.warning('get current server patch')
            server_patch = self._meteor_db.get_current_server_patch(self._lol.UPDATE_PLATFORM)
            self._logger.warning('save current client version related to server patch version')
            self._meteor_db.set_patch_version(self._lol.version, server_patch)
            self._logger.warning('get new lol patch version')
            self._playable_patch = self._lol_patch()
        self._logger.warning('upgrade finished new version = ' + self._lol.version)

    def _lol_patch(self):
        return self._patch_version.client_patch(self._lol.version)

    def get_pending_replays(self):
        replays = self._replay_manager.get_pending_replays()
        self._logger.debug('pending matches = {}'.format(len(replays)))
        return replays

    def replays_to_fact_replays(self, replays: [Replay]):
        fact_matches = []
        for replay in replays:
            fact_match = self._fact_db.get_fact_match(
                replay.platform_id,
                replay.game_id
            )
            if not fact_match:
                print("couldn't find match {} {}".format(replay.platform_id, replay.game_id))
                if datetime.now()-replay.record_timestamp > self._MAX_TIME_REPLAY_PENDING:
                    self._replay_manager.mark_as_handled_rep(replay.platform_id, replay.game_id)
                continue
            fact_matches.append(FactReplay(fact_match, replay))
            if len(fact_matches) >= self.MAX_MATCHES_PER_SCAN:
                break
        return fact_matches

    def fact_to_patch_matches(self, fact_matches: [FactMatch]):
        patch_matches = []
        print("fact_to_patch_matches patch {}".format(self._playable_patch))
        for fact_match in fact_matches:
            match_patch = self._patch_version.version_to_patch(fact_match.version)
            print("match {} {} patch {}".format(fact_match.platform_id, fact_match.game_id, match_patch))
            if match_patch == self._playable_patch:
                patch_matches.append(fact_match)
            elif match_patch < self._playable_patch:
                self._logger.warning('old replay found' +
                                     ' match patch: {}'.format(match_patch))
                self._logger.warning('playable patch: {}'.format(self._playable_patch))
                self._replay_manager.mark_as_handled_rep(
                    fact_match.platform_id,
                    fact_match.game_id
                )
            else:
                self._logger.debug('new match found {}/{}'
                                   .format(fact_match.platform_id,
                                           fact_match.game_id))
        self._logger.debug('patch matches = {}'.format(len(patch_matches)))
        return patch_matches

    @property
    def pending_patch(self):
        platform_patch = self._patch_version.version_to_patch(
            self._meteor_db.get_current_server_patch(
                self._lol.UPDATE_PLATFORM))
        return platform_patch != self._playable_patch

    def prepare_clips(self, match: FactMatch):
        events = generate_events(match)
        triple_timeout = timedelta(seconds=15)
        events = list(filter(lambda x: ((x.kills_in_row <= EventTripleKill.kills_in_row)
                                        or (match.duration - x.end_time >= triple_timeout)), events))
        return self._recorder.prepare_clips(events)

    def generate_clips(self, clips: [Clip], replay: SpectateMatch):
        clips = self._recorder.record_clips(clips, replay)
        if len(clips) > 0:
            sleep(self._OBS_FILE_HANDLE_WAIT_TIME)
        for clip in clips:
            self._store_service.upload(clip, self._upload_finished)

    def _upload_finished(self, clip: Clip):
        self._clip_store.store(clip)
        clip_folder = path.dirname(clip.video.path)
        rmtree(clip_folder)

    def match_rdy(self, match: Match):
        self._replay_manager.mark_as_handled_rep(
            match.platform_id,
            match.game_id)

    def start_downloads(self):
        self._replay_hoover.start()

    def stop_downloads(self):
        self._replay_hoover.stop()

    def is_downloading(self):
        return self._replay_hoover.get_num_downloads_in_progress() > 0

    def hoover_running(self):
        return self._replay_hoover.is_alive()

    def log_error(self, msg: str, error):
        self._logger.error('Error: {}'.format(error), exc_info=True)

    @property
    def logger(self):
        return self._logger

    def __del__(self):
        if self.is_downloading():
            self.stop_downloads()


if __name__ == '__main__':
    # init
    MIN_RUNTIME = timedelta(hours=8)
    start_time = datetime.now()
    meteor_db = Meteor('mongodb://replayer:qdgr4nlXF6IOy@88.99.138.8:27017/factdata?authSource=admin')
    clipper = Clipper(meteor_db)
    clipper.start_downloads()
    # clipper.logger.warning('hoover not started')
    clipper.logger.debug('run')
    try:
        while True:
            num_fuct_matches = 0
            patch_matches = []
            replays = clipper.get_pending_replays()
            clipper.logger.debug('num replays: {}'.format(len(replays)))
            replays_idx = 0
            replays_cutouts = []
            for ii in range(clipper.MAX_MATCHES_PER_SCAN, len(replays), clipper.MAX_MATCHES_PER_SCAN):
                cutout = replays[replays_idx:ii]
                print('cutout len {}'.format(len(cutout)))
                replays_cutouts.append(cutout)
                replays_idx = ii
            rest = replays[replays_idx:]
            replays_cutouts.append(rest)
            print('rest len: {}'.format(len(rest)))
            for replays_cutout in replays_cutouts:
                fact_matches = clipper.replays_to_fact_replays(replays_cutout)
                num_fuct_matches += len(fact_matches)
                patch_matches += clipper.fact_to_patch_matches(fact_matches)
                if len(patch_matches) >= clipper.MAX_MATCHES_PER_SCAN:
                    break
            if ((num_fuct_matches > 0)
                    and (len(patch_matches) == 0)
                    and clipper.pending_patch):
                clipper.upgrade_lol()
                break
            for match in patch_matches:
                clips = clipper.prepare_clips(match)
                if len(clips) > 0:
                    clipper.generate_clips(clips, match)
                clipper.match_rdy(match)
            if (datetime.now() - start_time) > MIN_RUNTIME:
                if not clipper.is_downloading():
                    break
            if not clipper.hoover_running():
                raise RuntimeError("hoover stoped working!")
            sleep(10)
    except Exception as err:
        clipper.logger.error('Error: {}'.format(err), exc_info=True)
    try:
        clipper.logger.warning('going for reboot')
        del clipper
    finally:
        # reboot
        system('shutdown -t 1 -r -f')
