import twitter
import pymongo
from pymongo import MongoClient

connection = MongoClient()
db = connection.test_database
tweets = db.tweets

CONSUMER_KEY = 'sLGccwOdfySptswo1ZKErg'
CONSUMER_SECRET = 'z5V9g6sOJ9BEYhvsSvnzt6pjS7gVWV2komWyIz5XZE'
oauth_token = "101769689-tPwXbgj96kaYpnCKHSijZJ5r6arePyLlMIQUj4Ts"
oauth_secret = "ijCLoaw3bfRiOzbR572jKGQe3pYHndIps3CIp9KOWa4"

twitter_stream = twitter.TwitterStream(auth=twitter.oauth.OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))
iterator = twitter_stream.statuses.sample()

for tweet in iterator:
    print(tweet)
    tweets.insert(tweet)
