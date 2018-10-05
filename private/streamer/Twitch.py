# coding: utf-8

import requests
from requests_oauthlib import OAuth2Session

from dateutil.parser import parse #pip install python-dateutil
import datetime

class Twitch:

    def __init__(self, refresh_token):
        self._refresh_token = refresh_token
        
        self._cacheVideo = None

        self.__twitch_client_id = 'mtuun74tffohdl6m6r79l6ijc4bcr9'
        self.__twitch_client_secret = '7eo4srojr2qcwwhuodqpq4xc1gfujf'
       
        self.__channel_id = '183733104'
       
    def _refresh_tokens(self, max_retries=3, retried=0):
        try:
            url = (r'https://api.twitch.tv/kraken/oauth2/token'
                '?client_id={}'
                '&client_secret={}'
                '&grant_type=refresh_token'
                '&refresh_token={}'.format(
                      self.__twitch_client_id, self.__twitch_client_secret, self._refresh_token))
            headers = {
                'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.post(url, headers=headers).json()

            self._access_token = r['access_token']
            self._refresh_token = r['refresh_token']
            self._scope = r['scope']
            self._expires_in = r['expires_in']
        except Exception as e:
            print('exception caught')
            if retried < max_retries:
                print('perform retry')
                self._refresh_tokens(max_retries, retried+1)
            else:
                print('max retries performed, tokens not refreshed', e)

    def set_title(self, title):
        self._refresh_tokens()
        url = r'https://api.twitch.tv/kraken/channels/{}'.format(self.__channel_id)
        headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': self.__twitch_client_id,
            'Authorization': 'OAuth {}'.format(self._access_token),
            'Content-Type': 'application/json'}
        data = '{{"channel": {{"status": "{}"}}}}'.format(title)

        requests.put(url, headers=headers, data=data)

    def set_live_notification(self, notification):
        pass # TODO Implementieren wir späters

    def get_video_ids(self, limit=100):
        if (limit > 100):
            raise Exception('limit ' + str(limit) + ' exceeds max limit 100')
        if (limit < 1):
            raise Exception('limit ' + str(limit) + ' - min limit 1')

        self._refresh_tokens()
        url = r'https://api.twitch.tv/kraken/channels/{}/videos?limit={}'.format(self.__channel_id, limit)
        headers = {
                'Accept': 'application/vnd.twitchtv.v5+json',
                'Client-ID': self.__twitch_client_id}
        r = requests.get(url, headers=headers).json()
        
        ids = []
        for video in r['videos']:
            if video['status'] == 'recorded':
                ids.append(video['_id'])

        return ids

    def _get_video_by_id(self, id):
        if (self._cacheVideo == None) or (self._cacheVideo['_id']!=id):
            url = r'https://api.twitch.tv/kraken/videos/{}'.format(id)
            headers = {
                    'Accept': 'application/vnd.twitchtv.v5+json',
                    'Client-ID': self.__twitch_client_id}
            self._cacheVideo = requests.get(url, headers=headers).json()

        return self._cacheVideo

    def get_video_time(self, id):
        video = self._get_video_by_id(id)
        length = datetime.timedelta(seconds=video['length'])
        print(video['created_at'])
        timestring = video['created_at'].replace('Z', '+0000')
        start = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')
        print('start: ' + str(int(start.timestamp())))
        print('video lenghth ' + str(length))
        print(str(start))
        return {
            'start':start,
            'stop':start+length}

    def get_video_url(self, id):
        return self._get_video_by_id(id)['url']