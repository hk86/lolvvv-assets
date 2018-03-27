import twitter #pip install python-twitter
#from pprint import pprint

import threading
from time import sleep

from Scoreboard import Scoreboard

class Twitter:

    def __init__(self, db):
        self._db = db
        self._scoreboard = Scoreboard()
        self._api = twitter.Api(consumer_key='yQXbcSeDzNpm41S0Zkk4SJe1E',
                            consumer_secret='m3YqCoE2gdUbw5sWiT9K1JweH6B030wbgIxFnbvzjc8h1kAotV',
                            access_token_key='975016856946991104-sRp0vNiAJos4jnQJUdSZDyrYLS5I0Kz',
                            access_token_secret='6SijNxsmEzgj4gqpFCoqCbbfovElo15wfHC4GmO9N2QNi')

    def _generateTweet(self, live_match):
        #something like this:
        # [KSV] CuVee & [EDG] Scout crushing SoloQ! NOW live on stream
        # https://www.lolvvv.com/live
        # ------------------------------
        # #CuVee as #Kassadin #Scout as #Zed
        # #lolvvv #live #stream #twitch #leagueoflegends #leagueoflegend #LoL

        tweet = live_match.getTitle(self._db) + ' NOW live on stream\n' + 'https://www.lolvvv.com/live\n'
        tweet += '------------------------------\n'

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

            tweet += ' as #' + self._db.getChampionKey(pro['championId']) + ' '

        tweet = tweet[:-1] + '\n#lolvvv #live #stream #twitch #leagueoflegends #leagueoflegend #LoL'

        return tweet
        
    def __tweeting(self, live_match):
        sleep(5)
        self._api.PostUpdate(self._generateTweet(live_match), media=self._scoreboard.get())

    def tweet(self, live_match):
        threading.Thread(target=self.__tweeting, args=(live_match))


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