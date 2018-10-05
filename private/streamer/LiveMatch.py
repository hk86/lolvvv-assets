# coding: utf-8

import datetime
import json
from Replay import Replay
#from pprint import pprint

class LiveMatch:
    
    def __init__(self, platform_id, game_id, encryption_key, db):
        PLATFORMS = json.load(open(r'../json/LolPlatforms.json'))
        match_platform = PLATFORMS[platform_id]
        self._db = db
        self._URL = match_platform['domain'] + ':' + match_platform['port']
        self._GAME_ID = game_id
        self._ENCRYPTION_KEY = encryption_key
        self._PLATFORM_ID = platform_id
        self.summoners = []

    def _get_platform_id(self):
        return self._PLATFORM_ID

    def _get_game_id(self):
        return self._GAME_ID

    def _get_encryption_key(self):
        return self._ENCRYPTION_KEY

    def _get_url(self):
        return self._URL
            
    def getPros(self):
        pros = []
        for player in self.summoners:
            if player['pro']:
                pros.append(player)
        return pros
        
    def getTeam(self, teamId):
        team = []
        for player in self.summoners:
            if player['teamId'] == teamId:
                team.append(player)
        
        return team
        
    def getBlueTeam(self):
        return self.getTeam(100)
        
    def getRedTeam(self):
        return self.getTeam(200)

    def _generateTeamTitle(self, teamId):
        teamTitle = None
        for player in self.summoners:
            if player['pro'] and player['teamId'] == teamId:
                fullName = ''
                proTeamId = self._db.getPro(player['pro']['proId'])['teamId']
                if proTeamId:
                    fullName = '[' + self._db.getTeamTag(self._db.getPro(player['pro']['proId'])['teamId']) + '] '
                fullName = fullName +  player['pro']['nickName']
                if not teamTitle:
                    teamTitle = fullName
                else:
                    teamTitle += ' & '
                    teamTitle += fullName
        return teamTitle

    def _generate_match_title(self):
        blueTeamTitle = self._generateTeamTitle(100)
        redTeamTitle = self._generateTeamTitle(200)
        pros = self.getPros()
        if ( len(pros) == 1):
            champName = self._db.getChampionName(pros[0]['championId'])
            if not blueTeamTitle:
                title = redTeamTitle
            else:
                title = blueTeamTitle
            title = title + ' with ' + champName
        else:
            emptyTeamTilte = ''
            if not blueTeamTitle:
                title = redTeamTitle + emptyTeamTilte
            elif not redTeamTitle:
                title = blueTeamTitle + emptyTeamTilte
            else:
                title = blueTeamTitle + ' vs. ' + redTeamTitle
        return title

    def getTitle(self):
        title = self._generate_match_title()
        return 'Pros: {}'.format(title)

    def getTwitchTitle(self):
        return (self._generate_match_title() + ' - lolvvv.com')

    def generate_replay(self):
        return Replay(self)

    def _get_db(self):
        return self._db

    meteor_db = property(fget=_get_db)
    platform_id = property(fget=_get_platform_id)
    game_id = property(fget=_get_game_id)
    encryption_key = property(fget=_get_encryption_key)
    url = property(fget=_get_url)