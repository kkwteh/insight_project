#!/Users/teh/code/insight_project/ENV/bin/python

import numpy as np
import twitter
import inflect
import pickle
import re
import string
import sets
import unicodedata
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

def init_data():
    f = open("top_twitter_words.pkl")
    top_twitter_words = pickle.load(f)
    return top_twitter_words


def init_twitter():
    f = open("twitter_oauth.pkl")
    cred = pickle.load(f)
    return twitter.Twitter(domain="search.twitter.com",
                    auth=twitter.oauth.OAuth(cred[0],cred[1],cred[2],cred[3]))


def slice_up(query):
    twitter_search = init_twitter()
    top_twitter_words = init_data()
    tweets = get_tweets(twitter_search, query)
    split_tweets = clean_tweets(tweets)
    count, keys = count_words_in_tweets(query, split_tweets, top_twitter_words)
    pickle_top_words(query, count, keys)
    return tweets, count, keys


def get_tweets(twitter_search, query):
    tweets = []
    num_pages = 16
    for i in range(1,num_pages):
        search = twitter_search.search(q=query, lang="en", page=str(i), rpp=100)
        for t in search[u'results']:
            ascii = get_ascii(t[u'text'])
            if re.search("RT",ascii) is None:
                tweets.append(ascii)
    print("Got tweets")
    return tweets


def clean_tweets(tweets):
    split_tweets = sets.Set()
    for tweet in tweets:
        tweet = re.sub("\ART", "", tweet)           #RT indicator
        tweet = re.sub("@\w*", "", tweet)           #@names
        tweet = re.sub("#\w*", "", tweet)           #hashtags
        tweet = re.sub("\S*\.\S+", "", tweet)       #link names, but not periods
        tweet = clean_punct(tweet)
        split_tweets.add(tuple(word_tokenize(tweet)))

    for split_tweet in split_tweets:
        for word in split_tweet:
            word = re.sub("\A['-\.]*", "", word)
            word = re.sub("['-\.]*\Z", "", word)
    return list(split_tweets)


def pickle_top_words(query, count, keys):
    just_counts = [count[key] for key in keys]
    a = np.array(just_counts)
    max_candidates = 100
    percentile = 100 * max(1 - (1.0 * max_candidates)/len(a),0)
    min((1.0 * max_candidates)/len(a),100)
    frequent_keys = [key for key in keys if count[key] > np.percentile(a,
                                                            percentile)]
    o = open("query_"+query+".pkl","wb")
    pickle.dump(frequent_keys, o, -1)
    o.close()


def count_words_in_tweets(query, split_tweets, top_twitter_words):
    common_many_words = 3000
    pairs = top_twitter_words[:common_many_words]
    low_information_words = [x[0] for x in pairs]
    cnt = Counter()
    high_cnt = Counter()

    for split_tweet in split_tweets:
        for word in split_tweet:
            #store words that are a) not low information words and do not
            #contain numbers and are not the query itself and
            #b) wn knows about or begin with a single
            #capital letter
            word
            if (word.lower() not in low_information_words and
                re.search("[0-9]",word) is None and
                word.lower() not in relatives(query.lower())):
                if wn.synsets(word) != []:
                    cnt[word.lower()] += 1
                elif re.search("\A[A-Z][^A-Z]*\Z",word) is not None:
                    cnt[word.lower()] += 1
    keys = [key for key in cnt]
    keys.sort(key=lambda k:-cnt[k])
    return cnt, keys

def relatives(query):
        infl = inflect.engine()
        return [query, infl.singular_noun(query), infl.plural(query)]


def clean_punct(tweet):
    safe_punct = ["'", "-"]
    for punct in string.punctuation:
        if punct not in safe_punct:
            tweet = tweet.replace(punct,"")
    return tweet


def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')
