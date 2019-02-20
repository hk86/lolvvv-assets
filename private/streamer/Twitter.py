import twitter  # pip install python-twitter
from pprint import pprint

import json
import threading
from time import sleep


class Twitter:

    def __init__(self, db, log):
        self._db = db
        self._log = log
        access_data = json.load(open('Twitter.json'))
        self._api = twitter.Api(consumer_key=access_data['consumer_key'],
                                consumer_secret=access_data['consumer_secret'],
                                access_token_key=access_data['access_token_key'],
                                access_token_secret=access_data['access_token_secret'])

    def _getTwitterTag4Pro(self, proId):
        twitterName = None
        twitterId = self._db.getTwitterId(proId)
        if twitterId:
            twitterName = self.getUserName(twitterId)

        if twitterName:
            twitterTag = ('@' + twitterName)
        else:
            twitterTag = '#' + self._db.getProKey(proId)
        return twitterTag

    def _generateTweet(self, live_match):
        # something like this:
        # [KSV] CuVee & [EDG] Scout crushing SoloQ! NOW live on stream
        # https://www.lolvvv.com/live
        # ------------------------------
        # #CuVee as #Kassadin #Scout as #Zed
        # #lolvvv #live #stream #twitch #leagueoflegends #leagueoflegend #LoL

        tweet = live_match.getTitle(self._db) + ' NOW live on stream\n' + 'https://www.lolvvv.com/live\n'
        tweet += '-----\n'

        for pro in live_match.getPros():
            tweet += self._getTwitterTag4Pro(pro['pro']['proId']) + ' '

            # tweet += ' as #' + self._db.getChampionKey(pro['championId']) + ' '

        tweet = tweet[:-1] + '\n#lolvvv #live #stream #twitch #leagueoflegends #LoL'

        return tweet

    def tweeting(self, live_match, scoreboard):
        msg = self._generateTweet(live_match)
        try:
            self._api.PostUpdate(msg, media=scoreboard.get())
        except twitter.error.TwitterError:
            self._log.warning('Error while posting msg:\n' + msg)

    def responseToTweet(self, live_match, scoreboard):
        msg = self._generateTweet(live_match)
        try:
            self._api.PostUpdate(msg, media=scoreboard.get(), in_reply_to_status_id=self._db.getMainTweetId())
        except twitter.error.TwitterError:
            self._log.warning('Error while posting msg:\n' + msg)

    def mainTweet(self):
        # something like this:
        # Stream on www.lolvvv.com/live (replied the current matches)
        # ---
        # Last 24h stats
        # Top 3 streamers: @FroggenLoL [10] @Jankos [8] @Ning [3]
        # Top 3 champs: #Swain [18] #Jhin [12] #LeeSin [9]
        # ---
        # #lolvvv #leagueoflegends #stream #twitch #live

        new_line = '\n'
        bar = '---' + new_line

        std_text = 'Stream on www.lolvvv.com/live (replied the current matches)' + new_line
        std_stats = 'Last 24h stats' + new_line
        std_hashes = '#lolvvv #leagueoflegends #stream #twitch #live'

        limit = 3

        streamers = self._db.getMostShownProLast24Hours(limit)
        streamers_txt = 'Top ' + str(limit) + ' streamers: '

        for pro in streamers:
            streamers_txt += self._getTwitterTag4Pro(pro['proId']) + ' '
            streamers_txt += '[' + str(pro['count']) + '] '

        streamers_txt = streamers_txt[:-1] + new_line

        champs = self._db.getMostPlayedChampsLast24Hours(limit)
        champs_txt = 'Top ' + str(limit) + ' champs: '

        for champ in champs:
            champs_txt += '#' + champ['championKey'] + ' '
            champs_txt += '[' + str(champ['count']) + '] '

        champs_txt = champs_txt[:-1] + new_line

        msg = std_text + bar + std_stats + streamers_txt + champs_txt + bar + std_hashes
        print(msg)

        msgId = self._api.PostUpdate(msg).AsDict()['id']
        self._db.updateMainTweet(msgId)

    def follow(self, twitterId):
        try:
            self._api.CreateFriendship(user_id=twitterId, retweets=False)
        except twitter.error.TwitterError:
            print('twitter error at id ' + str(twitterId))
            print('proId: ' + str(
                self._db.getProIdByTwitterId(twitterId)) + ' nickname: ' + self._db.getProNicknameByTwitterId(
                twitterId))

    def getUserName(self, twitterId):
        try:
            qry = self._api.GetUser(twitterId)
        except twitter.error.TwitterError:
            return None
        return qry.screen_name
