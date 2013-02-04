import pymongo
from pymongo import MongoClient
import string
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
import pickle
import unicodedata
import re
from nltk.corpus import wordnet as wn
def main():
    connection = MongoClient()
    db = connection.test_database
    tweets = db.tweets
    en_tweets_cursor = tweets.find({"lang": "en"})
    stepper = display_count()
    tweets = load_tweets(en_tweets_cursor, stepper)
    cnt = count_words_in_tweets(tweets, stepper)
    output = open('twitter_word_count.pkl', 'wb')
    d = dict(cnt)
    pickle.dump(d, output, -1)
    output.close()

def display_count():
    i = [0]
    def f():
        i[0] += 1
        if i[0] % 1000 == 0:
            print("Step: " + str(i[0]))
    return f

def load_tweets(en_tweets_cursor, stepper):
    tweets = []
    for tweet in en_tweets_cursor:
        stepper()
        text = get_ascii(tweet[u'text'])
        tweets.append(text)
    return tweets

def count_words_in_tweets(tweets, stepper):
    cnt = Counter()

    for tweet in tweets:
        stepper()
        words_of_tweet = wordpunct_tokenize(tweet)

        for word in words_of_tweet:
            cnt[word.lower()] += 1
    return cnt

def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')

if '__main__' == __name__:
    main()
