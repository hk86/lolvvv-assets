import twitter #pip install python-twitter
#from pprint import pprint

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

    def _generateTweet(self, live_match):
        #something like this:
        # [KSV] CuVee & [EDG] Scout crushing SoloQ! NOW live on stream
        # https://www.lolvvv.com/live
        # ------------------------------
        # #CuVee as #Kassadin #Scout as #Zed
        # #lolvvv #live #stream #twitch #leagueoflegends #leagueoflegend #LoL

        tweet = live_match.getTitle(self._db) + ' NOW live on stream\n' + 'https://www.lolvvv.com/live\n'
        tweet += '-----\n'

        for pro in live_match.getPros():
            twitterName = None
            proId = pro['pro']['proId']
            twitterId = self._db.getTwitterId(proId)
            if twitterId:
                twitterName = self.getUserName(twitterId)

            if twitterName:
                tweet += '@' + twitterName
            else:
                tweet += '#' + self._db.getProKey(proId)

            tweet += ' '

            #tweet += ' as #' + self._db.getChampionKey(pro['championId']) + ' '

        tweet = tweet[:-1] + '\n#lolvvv #live #stream #twitch #leagueoflegends #LoL'

        return tweet
        
    def tweeting(self, live_match, scoreboard):
        msg = self._generateTweet(live_match)
        try:
            self._api.PostUpdate(msg, media=scoreboard.get())
        except twitter.error.TwitterError:
            self._log.warning('Error while posting msg:\n' + msg)

    def tweet(self, live_match):
        # That doesn't work currently
        threading.Thread(target=self.tweeting, args=(live_match,)).start()


    def follow(self, twitterId):
        try:
            self._api.CreateFriendship(user_id=twitterId,retweets=False)
        except twitter.error.TwitterError:
            print('twitter error at id ' + str(twitterId))
            print('proId: ' + str(self._db.getProIdByTwitterId(twitterId)) +  ' nickname: ' + self._db.getProNicknameByTwitterId(twitterId))

    def getUserName(self, twitterId):
        try:
            qry = self._api.GetUser(twitterId)
        except twitter.error.TwitterError:
            return None
        return qry.screen_name