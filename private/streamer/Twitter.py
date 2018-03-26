import twitter #pip install python-twitter
#from pprint import pprint

from Scoreboard import Scoreboard

class Twitter:

    def __init__(self, db, scoreboard):
        self._db = db
        self._scoreboard = Scoreboard()
        self._api = twitter.Api(consumer_key='yQXbcSeDzNpm41S0Zkk4SJe1E',
                            consumer_secret='m3YqCoE2gdUbw5sWiT9K1JweH6B030wbgIxFnbvzjc8h1kAotV',
                            access_token_key='975016856946991104-sRp0vNiAJos4jnQJUdSZDyrYLS5I0Kz',
                            access_token_secret='6SijNxsmEzgj4gqpFCoqCbbfovElo15wfHC4GmO9N2QNi')

    def _generateTweet(self, pros):
        #something like this: @Faker (#Kaisa), @Rekkles (#Swain), @Cabochard (#Gangplank) NOW live on stream https://www.lolvvv.com/live #lolvvv #

        tweet = ''

        for pro in pros:
            twitterName = None
            proId = pro['pro']['proId']
            twitterId = self._db.getTwitterId(proId)
            if twitterId:
                twitterName = self.getUserName(twitterId)

            if twitterName:
                tweet += '@' + twitterName
            else:
                tweet += '#' + self._db.getProKey(proId)

            tweet += ' (#' + self._db.getChampionKey(pro['championId']) + '), '

        tweet = tweet[:-2] + ' NOW live on stream https://www.lolvvv.com/live #lolvvv #leagueoflegends #twitch'

        return tweet
        

    def tweet(self, pros):
        self._api.PostUpdate(self._generateTweet(pros), self._scoreboard.get())


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