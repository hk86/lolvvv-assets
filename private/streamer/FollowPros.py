from Twitter import Twitter
from Database import Database
from pprint import pprint


if __name__ == "__main__":

    db = Database('mongodb://root:ZTgh67gth1@10.8.0.6:27017/meteor?authSource=admin')

    twitterIds = db.getAllTwitterIds()

    twitter = Twitter(db)

    for id in twitterIds:
        twitter.follow(id)

    print('finished')
