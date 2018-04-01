import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamer'))

from Database import Database
from Logger import Logger
from Twitter import Twitter

if __name__ == "__main__":
    db = Database('mongodb://root:ZTgh67gth1@10.8.0.6:27017/meteor?authSource=admin')
    logger = Logger('twitterApp')

    twitter = Twitter(db, logger)
    twitter.mainTweet()

    logger.info('finished')