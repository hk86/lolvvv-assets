import twitter #pip install python-twitter
from pprint import pprint

class Twitter:

    def __init__(self, db):
        self._db = db
        self._api = twitter.Api(consumer_key='yQXbcSeDzNpm41S0Zkk4SJe1E',
                            consumer_secret='m3YqCoE2gdUbw5sWiT9K1JweH6B030wbgIxFnbvzjc8h1kAotV',
                            access_token_key='975016856946991104-sRp0vNiAJos4jnQJUdSZDyrYLS5I0Kz',
                            access_token_secret='6SijNxsmEzgj4gqpFCoqCbbfovElo15wfHC4GmO9N2QNi')


    def tweet(self, pros):
        subqry = api.GetUser(905753281162600449)
        print(subqry.screen_name)
        #status = api.PostUpdate('@lolvvv_com this is an app test')

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