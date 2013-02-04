#!/Users/teh/code/insight_project/ENV/bin/python
import sys
import itertools
import numpy as np
import time
import twitter
import inflect
import pickle
import re
import os
import string
import sets
import unicodedata
import threading
import urllib2
import pages_getter
from Queue import Queue
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import wordnet as wn

def init_data():
    f = open("top_twitter_words.pkl")
    top_pairs= pickle.load(f)
    top_words = [pair[0] for pair in top_pairs]
    return top_words


def slice_up(query):
    twitter_search = pages_getter.init_twitter()
    top_twitter_words = init_data()

    num_pages = 15
    per_page = 100
    query_list = [query for i in range(num_pages)]
    page_nums = [i + 1 for i in range(num_pages)]
    pages_with_queries = pages_getter.get_pages_of_tweets(twitter_search, query_list, page_nums, per_page)
    pages = [pair[1] for pair in pages_with_queries]
    print "finished download"
    full_tweets = flatten(pages)
    print "flattened pages"
    tweets = [get_ascii(t[u'text']) for t in full_tweets]
    print "got tweets"
    split_tweets = clean_tweets(tweets)
    print "cleaned tweets"
    capital_count, count, keys = count_words_in_tweets(query, split_tweets, top_twitter_words)
    print "counted words"
    top_results = extract_top_results(query, capital_count, count, keys)
    print "extracted top results"
    return tweets, count, keys, top_results

def flatten(pages):
    return list(itertools.chain.from_iterable(pages))

def clean_tweets(tweets):
    split_tweets = sets.Set()
    for tweet in tweets:
        tweet = re.sub("\ART", "", tweet)           #RT indicator
        tweet = re.sub("@\w*", "", tweet)           #@names
        tweet = re.sub("#\w*", "", tweet)           #hashtags
        tweet = re.sub("\S*\.\S+", "", tweet)       #link names, but not periods
        split_tweets.add(tuple(wordpunct_tokenize(tweet)))


    return list(split_tweets)


    # capital_frac = [(key, capital_cnt[key] * 1.0 / cnt[key]) for key in capital_cnt if cnt[key] > 1]
    # capital_frac = [(a,b) for (a,b) in capital_frac if 0.5 <= b and b<1.0]
    # capital_frac.sort(key= lambda (a,b): -cnt[a])
    # num_candidates = 10
    # top_results = [a for (a,b) in capital_frac[:num_candidates]]
    # return top_results


def extract_top_results(query, capital_cnt, cnt, keys):
    capital_frac = [(key, capital_cnt[key] * 1.0 / cnt[key]) for key in capital_cnt if cnt[key] > 1]
    capital_frac = [(a,b) for (a,b) in capital_frac if 0.5 <= b and b<1.0]
    capital_frac.sort(key= lambda (a,b): -cnt[a])
    just_counts = [cnt[key] for key in keys]
    a = np.array(just_counts)
    max_capital_candidates = 5
    max_heavy_candidates = 5
    heavy_factor = 0.005
    capital_candidates = [a for (a,b) in capital_frac[:max_capital_candidates]]
    heavy_candidates = [key for key in cnt if cnt[key] > heavy_factor * sum(just_counts) and key not in capital_candidates]
    heavy_candidates.sort(key= lambda w: -cnt[w])
    heavy_candidates = heavy_candidates[:max_heavy_candidates]
    top_results = heavy_candidates + capital_candidates
    top_results.sort(key = lambda w: -cnt[w])
    return top_results


def count_words_in_tweets(query, split_tweets, top_twitter_words):
    low_information_words = top_twitter_words
    cnt = Counter()
    capital_cnt = Counter()
    for split_tweet in split_tweets:
        for word in split_tweet:
            if (word.lower() not in low_information_words and
            re.search("[0-9\W]",word) is None and
            related(word.lower(),query.lower()) is not True and
            len(word) > 2):
                cnt[word.lower()] += 1
                if len(re.findall("\A[A-Z]", word)) == 1:
                    capital_cnt[word.lower()] += 1
    keys = [key for key in cnt]
    keys.sort(key=lambda k:-cnt[k])
    return capital_cnt, cnt, keys




def related(word1, word2):
        if (word1.find(word2) == -1 and
            word2.find(word1) == -1):
            return False
        else:
            return True


def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')
