import json
import requests
import shutil
from match import Match

class SpectateClient:

    def __init__(self, live_match:Match):
        self._live_match = live_match
        self._URL_PREFIX = r'http://{}/observer-mode/rest/consumer/'.format(
            self._live_match.url)

    def get_game_meta_data(self):
        url = self._prepare_token_req('getGameMetaData', 0)
        return (self._request_json(url))

    def get_platform_version(self):
        return (self._request('version').text)

    def get_chunk_info(self, chunk_id):
        url = self._prepare_token_req('getLastChunkInfo', chunk_id)
        return self._request_json(url)
    
    def get_chunk_data(self, chunk_id):
        url = self._prepare_token_req('getGameDataChunk', chunk_id)
        return self._request(url, True)

    def get_key_frame(self, key_frame_id):
        url = self._prepare_token_req('getKeyFrame', key_frame_id)
        return self._request(url, True)

    def get_end_stats(self):
        url = r'endOfGameStats/{}/{}/null'.format(
            self._live_match.platform_id,
            self._live_match.game_id)
        return self._request_media_data(url)

    def _request(self, req_parameters, stream=False):
        url = self._URL_PREFIX + req_parameters
        response = requests.get(url, stream=stream)
        if (response.status_code == 200):
            return response
        else:
            return None

    def _request_json(self, req_parameters):
        r = self._request(req_parameters)
        if r:
            return r.json()
        else:
            return None

    def _request_media_data(self, req_parameters):
        r = self._request(req_parameters, True)
        if r:
            return r.content
        else:
            return None
        
    
    def _prepare_token_req(self, kind, _id):
        url = r'{}/{}/{}/{}/token'.format(
            kind,
            self._live_match.platform_id,
            self._live_match.game_id,
            _id)
        return (url)