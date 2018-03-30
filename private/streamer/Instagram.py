#!/usr/bin/env python

from InstagramAPI import InstagramAPI

class Instagram:

    def __init__(self, db, scoreboard):
        self._db = db
        self._scoreboard = scoreboard
        self._api = InstagramAPI("lolvvv_com_live", "r94UP9fh3")
        self._api.login()  # login

    def generateArticle(self, live_match):
        photo_path = self._scoreboard.getForInsta()
        title = live_match.getTitle(self._db) + '!\n'
        std_hashes = '#leagueoflegends #lolesports #riotgames #lolvvv '

        pro_hashes = ''
        champ_hashes = ''

        for pro in live_match.getPros():
            pro_hashes += '#' + self._db.getProKey(proId) + ' '
            champ_hashes += '#' + self._db.getChampionKey(pro['championId']) + ' '

        champ_hashes = champ_hashes[:-1] # remove space
        caption = title + '\n\nStream-Link in Bio!\n\n\n' + std_hashes + pro_hashes + champ_hashes
        InstagramAPI.uploadPhoto(photo_path, caption=caption)