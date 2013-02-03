import pymongo
from pymongo import MongoClient

connection = MongoClient()
db = connection.test_database
tweets = db.tweets

# for tweet in tweets.find():
#     print(tweet)

print(tweets.count())
print(tweets.find({"lang": "en"}).count())
