# coding: utf-8

import requests
from requests_oauthlib import OAuth2Session

class Twitch:

   def __init__(self, refresh_token):
       self._refresh_token = refresh_token
       
       self.__twitch_client_id = 'mtuun74tffohdl6m6r79l6ijc4bcr9'
       self.__twitch_client_secret = '7eo4srojr2qcwwhuodqpq4xc1gfujf'
       
       self.__channel_id = '183733104'
       
   def _refresh_tokens(self):
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
       pass # TODO Implementieren wir sp�ter