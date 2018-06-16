from datetime import datetime
from time import sleep
import json

from SpectateClient import SpectateClient

import logging

class ReplayDownloader():

    def __init__(self, replay):
        self._replay = replay
        self._spectate_client = SpectateClient(self._replay.live_match)
        self._last_chunk_info = {}
        self._download_retries = 0
        self._last_chunk_id = 0
        self._last_key_frame_id = 0
        self._metas = None
        self._first_val_chunk_id = 0
        self._RETRIES_LIMIT = 5
        self._SLEEP_TIME_S = 1
        # Max 2 minutes in the past * 2 chunks/minute
        self._PAST_CHUNKS_LIMIT = 2*2
        logging.getLogger("requests").setLevel(logging.WARNING)


    def download(self):
        self._download_metas()
        self._validate_metas()
        self._get_last_chunk_infos()
        self._replay.last_chunk_infos(self._last_chunk_info)
        self._metas['pendingAvailableChunkInfo'] = []
        self._download_chunks()
        self._metas['pendingAvailableKeyFrameInfo'] = []
        self._download_key_frames()
        self._download_current_data()
        self._replay.metas = self._update_metas()

    def state(self):
        last_info = self._last_chunk_info
        if ((last_info['endGameChunkId'] != 0) and
            (last_info['endGameChunkId'] <= self._last_chunk_id)):
            # download has finished
            num_data_chunks = len(self._metas['pendingAvailableChunkInfo'])
            if (last_info['endGameChunkId'] == num_data_chunks):
                return 'complete'
            else:
                return 'incomplete'
        else:
            return 'downloading'

    def _download_metas(self):
        metas = self._spectate_client.get_game_meta_data()
        self._metas = metas

    def _validate_metas(self, tries=0):
        if((len(self._metas['pendingAvailableKeyFrameInfo'])) < 1):
            if (tries == 0):
                logging.info('looks like game is not started now')
                logging.info('waiting for the ingame 3rd minute...')
            if(tries < 20):
                WAITING_3RD_MIN_S = 30
                logging.info('_validate_metas going sleep for {} s'
                             .format(WAITING_3RD_MIN_S))
                sleep(WAITING_3RD_MIN_S)
                tries = tries + 1
                self._download_metas()
                return self._validate_metas(tries)
            raise Exception('The game is not yet available for spectator')
        if(self._metas['gameEnded']):
            raise Exception('The game has already ended, cannot download it')

    def _get_last_chunk_infos(self, chunk_id=0, tries=0):
        last_info = self._spectate_client.get_chunk_info(chunk_id)
        # validate Info
        if ((not last_info['chunkId']) or (last_info['chunkId'] == 0)):
            if (not last_info['chunkId']):
                self._add_download_retry()
            else:
                if (tries > 10):
                    raise Exception('The game is not started')
                logging.info('Couldn\'t get last chunk info.'\
                   + 'Going for sleep for 30 s')
                sleep(25) # 25 + 5 below
            sleep(5)
            return self._get_last_chunk_infos(chunk_id, tries)
        self._reset_download_retry()
        self._last_chunk_info = last_info
        return last_info

    def _download_key_frames(self):
        start = int((self._first_val_chunk_id - self._metas['startGameChunkId'])
            /2 + 1)
        logging.info('first key frame: ' + str(start))
        if start < 1:
            start = 1
        stop = self._last_chunk_info['keyFrameId']
        for ii in range(start, stop+1):
            self._download_key_frame(ii)

    def _download_key_frame(self, key_frame_id):
        key_frame = self._spectate_client.get_key_frame(key_frame_id)
        if key_frame:
            now = datetime.utcnow().strftime('%b %d, %Y %I:%M:%S %p')
            self._replay.add_key_frame(key_frame_id, key_frame)
            next_last_chunk_id = ((key_frame_id - 1)*2
                             + self._metas['startGameChunkId'])
            self._metas['pendingAvailableKeyFrameInfo'].append({
                    'id': key_frame_id,
                    'receivedTime':now,
                    'nextChunkId':next_last_chunk_id})
            self._last_key_frame_id = key_frame_id
            logging.info('key_frame_id ' + str(key_frame_id) + ' downloaded')
        else:
            if self._add_download_retry():
                logging.info('Couldn\'t get key_frame. Going for sleep for {}s'
                      .format(self._SLEEP_TIME_S))
                sleep(self._SLEEP_TIME_S)
                return self._download_key_frame(key_frame_id)
            else:
                logging.info('_download_key_frame invalid key_frame_id '
                      + str(key_frame_id))
        self._reset_download_retry()
        

    def _download_current_data(self):
        last_info = self._get_last_chunk_infos(self._last_chunk_id)
        if ((last_info['endGameChunkId'] != 0) and
            (last_info['endGameChunkId'] <= self._last_chunk_id)):
            logging.info('_download_current_data end stats')
            # end stats
            return
        if last_info['chunkId'] > self._last_chunk_id :
            downloadable_last_chunk_id = self._last_chunk_id + 1
            self._download_chunk(downloadable_last_chunk_id)
        if last_info['keyFrameId'] > self._last_key_frame_id :
            downloadable_last_key_frame_id = self._last_key_frame_id + 1
            self._download_key_frame(downloadable_last_key_frame_id)
        if ((last_info['chunkId'] > self._last_chunk_id) or
            (last_info['keyFrameId'] > self._last_key_frame_id)):
            return self._download_current_data()
        # nextAvailableChunk is in milliseconds
        seconds = (last_info['nextAvailableChunk'] + 500)/1000
        logging.info('waiting for next available chunk '\
            + 'going to sleep for ' + str(seconds) + 's')
        sleep(seconds)
        self._download_current_data()

    def _find_key_frame_by_last_chunk_id(self, chunk_id, raise_exception=False):
        for key_frame in self._metas['pendingAvailableKeyFrameInfo']:
            if(chunk_id == key_frame['nextChunkId']):
                return key_frame['id']
        if(raise_exception):
            logging.info('No key frame id found for chunk id: ' + str(chunk_id))
            raise Exception('No keyframe found for chunk {}'.format(chunk_id))
        return self._find_key_frame_by_last_chunk_id(chunk_id-1, True)

    def _download_chunks_range(self, dl_range):
        for ii in dl_range:
            self._download_chunk(ii)

    def _download_chunks(self):
        end = self._last_chunk_info['chunkId']
        if end > 6:
            self._download_chunks_range(range(1,3))
            # the first 2 chunks are always available
            start = end - self._PAST_CHUNKS_LIMIT
        else:
            start = 1
        self._download_chunks_range(range(start, (end + 1)))
        self._first_val_chunk_id = start

    def _find_first_last_chunk_id(self):
        chunks = []
        metas = self._metas
        start_game_last_chunk_id = metas['startGameChunkId']
        logging.info('startGameChunkId: ' + str(start_game_last_chunk_id))
        for chunk_info in metas['pendingAvailableChunkInfo']:
            if (chunk_info['id'] >= start_game_last_chunk_id):
                chunks.append(chunk_info)
        chunks.sort(key=lambda x: x['id'], reverse=True)
        # 55-54-53-51-50, will return 53 because 52 is missing
        # 55-54-53, will return 53
        chunk_id = None
        try:
            for idx, chunk in enumerate(chunks, 1):
                chunk_id = chunk['id']
                if chunk['id'] != chunks[idx]['id'] + 1:
                    break
        except IndexError:
            pass
        if ((not chunk_id)
            or (len(metas['pendingAvailableKeyFrameInfo']) < 1)):
            with open('ErrorFirstChunkId.json', 'w') as outfile:
                json.dump(metas['pendingAvailableChunkInfo'], outfile)
            logging.info('available info: ' + str(len(metas['pendingAvailableKeyFrameInfo'])))
            raise Exception('No first chunk id was found')
        next_last_chunk_id = metas['pendingAvailableKeyFrameInfo'][0]['nextChunkId']
        if (chunk_id < next_last_chunk_id):
            # if no keyframe is available for selected chunk
            chunk_id = next_last_chunk_id
        else:
            # if chunk is in the middle of keyframe (we take the next chunk)
            found = False
            for keyframe in metas['pendingAvailableKeyFrameInfo']:
                if (keyframe['nextChunkId'] == chunk_id):
                    found = True
                    break
            if (found):
                chunk_id = chunk_id + 1
        return chunk_id

    def _download_chunk(self, chunk_id):
        chunk_data = self._spectate_client.get_chunk_data(chunk_id)
        num_last_chunk_infos = len(self._metas['pendingAvailableChunkInfo'])
        if chunk_data:
            now = datetime.utcnow()
            #if num_last_chunk_infos < 1:
            #    self._metas['startGameChunkId'] = chunk_id
            self._replay.add_chunk(chunk_id, chunk_data)
            if self._last_chunk_info['chunkId'] == chunk_id:
                duration = self._last_chunk_info['duration']
            else:
                duration = 30000
            self._metas['pendingAvailableChunkInfo'].append({
                'duration': duration,
                'id': chunk_id,
                'receivedTime':now.strftime('%b %d, %Y %I:%M:%S %p')})
            self._last_chunk_id = chunk_id
            logging.info('_download_chunk(' + str(chunk_id) + ') downloaded')
        else:
            if self._add_download_retry():
                logging.info('Couldn\'t get chunk. Going for sleep for {}s'
                      .format(self._SLEEP_TIME_S))
                sleep(self._SLEEP_TIME_S)
                return self._download_chunk(chunk_id)
            else:
                logging.info('_download_chunk(' + str(chunk_id) + ') invalid chunk_id')
        self._reset_download_retry()

    def _update_metas(self):
        end_metas = self._spectate_client.get_game_meta_data()
        if self.state() == 'complete':
            first_chunk_id = end_metas['startGameChunkId']
        else:
            first_chunk_id = self._find_first_last_chunk_id()
        metas = {
            'firstChunkId': first_chunk_id,
            'endStartupChunkId': end_metas['endStartupChunkId'],
            'startGameChunkId': end_metas['startGameChunkId'],
            'endGameChunkId': self._last_chunk_id,
            'endGameKeyFrameId': self._last_key_frame_id
            }
        return metas

    def _add_download_retry(self):
        self._download_retries = self._download_retries + 1
        return (self._download_retries <= self._RETRIES_LIMIT)

    def _reset_download_retry(self):
        self._download_retries = 0