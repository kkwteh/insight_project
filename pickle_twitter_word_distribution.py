import pymongo
from pymongo import MongoClient
import string
from collections import Counter
from nltk.tokenize import wordpunct_tokenize
import pickle

connection = MongoClient()
db = connection.test_database
tweets = db.tweets
en_tweets_cursor = tweets.find({"lang": "en"})

i = 0
for tweet in en_tweets_cursor:

    text = tweet[u'text']

    for punct in string.punctuation:
        text = text.replace(punct,"")

    words_of_text = wordpunct_tokenize(text)
    cnt = Counter()
    for word in words_of_text:
        cnt[word] += 1

    i += 1
    if i >= 100:
        break

output = open('twitter_word_count.pkl', 'wb')
pickle.dump(cnt, output, -1)
output.close()
