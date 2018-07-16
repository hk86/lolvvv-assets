# coding: utf-8

import datetime
import json
from .match import Match
from match.replay import Replay
#from pprint import pprint

class LiveMatch(Match):
    
    def __init__(self, platform_id, game_id, encryption_key, meteor_db):
        Match.__init__(
            self, platform_id,
            game_id, encryption_key)
        self._db = meteor_db
        self.summoners = []
            
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
        pyke_ingame = False
        PYKE_CHAMPION_ID = 555
        for player in self.summoners:
            if player['championId'] == PYKE_CHAMPION_ID:
                pyke_ingame = True
        if pyke_ingame:
            title = 'Pros playing Pyke: {}'.format(title)
        else:
            title = 'Pros: {}'.format(title)
        return title

    def getTwitchTitle(self):
        return (self._generate_match_title() + ' - lolvvv.com')

    def _get_db(self):
        return self._db

    meteor_db = property(fget=_get_db)