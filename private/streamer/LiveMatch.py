import datetime
import pprint

class LiveMatch:
	
	def __init__(self, match):
		
		PLATFORM = {
			'NA1': {
				'domain': 'spectator.na.lol.riotgames.com',
				'port': '80'
			} ,
			'EUW1': {
				'domain': 'spectator.euw1.lol.riotgames.com',
				'port': '80'
			} ,
			'EUN1': {
				'domain': 'spectator.eu.lol.riotgames.com',
				'port': '8088'
			} ,
			'JP1': {
				'domain': 'spectator.jp1.lol.riotgames.com',
				'port': '80'
			} ,
			'KR': {
				'domain': 'spectator.kr.lol.riotgames.com',
				'port': '80'
			} ,
			'OC1': {
				'domain': 'spectator.oc1.lol.riotgames.com',
				'port': '80'
			} ,
			'BR1': {
				'domain': 'spectator.br.lol.riotgames.com',
				'port': '80'
			} ,
			'LA1': {
				'domain': 'spectator.la1.lol.riotgames.com',
				'port': '80'
			} ,
			'LA2': {
				'domain': 'spectator.la2.lol.riotgames.com',
				'port': '80'
			} ,
			'RU': {
				'domain': 'spectator.ru.lol.riotgames.com',
				'port': '80'
			} ,
			'TR1': {
				'domain': 'spectator.tr.lol.riotgames.com',
				'port': '80'
			} ,
			'PBE1': {
				'domain': 'spectator.pbe1.lol.riotgames.com',
				'port': '8088'
			}
		}
		
		time_s = match['gameStartTime']/1000
		print(time_s)
		print(datetime.datetime.fromtimestamp(time_s).strftime('%Y-%m-%d %H:%M:%S.%f'))
		
		match_platform = PLATFORM[match['platformId']]
		self.url = match_platform['domain'] + ':' + match_platform['port']
		self.gameId = match['gameId']
		self.encryptionKey = match['observers']['encryptionKey']
		self._id = match['_id']
		self.platformId = match['platformId']
		self.match = match
	
	def getUrl(self):
		return self.url

	def getGameId(self):
		return self.gameId
		
	def getEncKey(self):
		return self.encryptionKey
		
	def getPlatform(self):
		return self.platformId
		
	def stillRunning(self, active_matches):
		if active_matches.find({'_id': self._id}).count() > 0:
			return True
		else:
			return False
			
	def getPros(self, staticdata):
		pros = []
		for player in self.match['participants']:
			if staticdata['static_pros'].find({'summoners.'+str(self.platformId):player['summonerId']}).count() > 0:
				pros.append(player)
		return pros
		
	def getTeam(self, teamId):
		team = []
		for player in self.match['participants']:
			if player['teamId'] == teamId:
				team.append(player)
		
		return team
		
	def getBlueTeam(self):
		return self.getTeam(100)
		
	def getRedTeam(self):
		return self.getTeam(200)

	def _generateTeamTitle(self, team, pros, nicknames):
		teamTitle = None
		for ii, match_pro in enumerate(pros):
			for player in team:
				if player['summonerId'] == match_pro['summonerId']:
					if not teamTitle:
						teamTitle = nicknames[ii]
					else:
						teamTitle += ' & '
						teamTitle += nicknames[ii]
		return teamTitle
		
	def getTitle(self, staticdata):
		pros = self.getPros(staticdata)
		
		nickname = []
		
		for match_pro in pros:
			nickname.append(staticdata['static_pros'].find_one({'summoners.'+str(self.platformId):match_pro['summonerId']})['nickName'])
		
		if (len(pros) == 1):
			champ = staticdata['static_champions'].find_one({'id':pros[0]['championId']})
			title = nickname[0] + ' rocks with ' + champ['name']
		else:
			blueTeamTitle = self._generateTeamTitle(self.getBlueTeam(), pros, nickname)
			redTeamTitle = self._generateTeamTitle(self.getRedTeam(), pros, nickname)
			
			emptyTeamTilte = ' vs the world!!!'
			
			if not blueTeamTitle:
				title = redTeamTitle + emptyTeamTilte
			elif not redTeamTitle:
				title = blueTeamTilte + emptyTeamTilte
			else:
				title = blueTeamTitle + ' VS ' + redTeamTitle
				
			
		return ('lolvvv.com - ' + title)
		
		
	def one(self, pro, staticdata):
		pro = staticdata['static_pros'].find({'summoners'.self.platformId:player['summonerId']})
		return 
