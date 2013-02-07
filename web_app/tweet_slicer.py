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


def slice_up(query, num_results):
    twitter_search = pages_getter.init_twitter()
    top_twitter_words = init_data()

    num_pages = 15
    per_page = 100
    query_list = [query for i in range(num_pages)]
    page_nums = [i + 1 for i in range(num_pages)]
    pages_with_queries = pages_getter.get_pages_of_tweets(twitter_search, query_list, page_nums, per_page)
    pages = [pair[1] for pair in pages_with_queries]
    tweets = flatten(pages)
    for tweet in tweets:
        tweet['text'] = get_ascii(tweet[u'text'])
    split_tweets = clean_tweets(query, tweets)
    capital_count, count, keys = count_words_in_tweets(query, split_tweets, top_twitter_words)
    top_results = extract_top_results(query, num_results, capital_count, count, keys)
    return tweets, count, keys, top_results

def flatten(pages):
    return list(itertools.chain.from_iterable(pages))

def clean_tweets(query, tweets):
    split_tweets = sets.Set()
    query_words = query.split()

    for tweet in tweets[:]:
        if related([tweet['text'].lower()], query_words):
            tweet['text'] = re.sub("\ART", "", tweet['text'])
            tweet['text'] = re.sub("@\w*", "", tweet['text'])
            tweet['text'] = re.sub("#\w*", "", tweet['text'])
            tweet['text'] = re.sub("\S*\.\S+", "", tweet['text'])
            split_tweets.add(tuple(wordpunct_tokenize(tweet['text'])))
        else:
            tweets.remove(tweet)
    return list(split_tweets)


def extract_top_results(query, num_results, capital_cnt, cnt, keys):
    capital_frac = [(key, capital_cnt[key] * 1.0 / cnt[key]) for key in capital_cnt if cnt[key] > 1]
    capital_frac = [(a,b) for (a,b) in capital_frac if 0.5 <= b and b<1.0]
    capital_frac.sort(key= lambda (a,b): -cnt[a])
    just_counts = [cnt[key] for key in keys]
    a = np.array(just_counts)

    total_candidates = num_results
    max_heavy_candidates = int(0.4 * total_candidates)
    heavy_factor = 0.005

    heavy_candidates = [key for key in cnt if (cnt[key] > heavy_factor *
                                                sum(just_counts))]
    heavy_candidates.sort(key= lambda w: -cnt[w])
    heavy_candidates = heavy_candidates[:max_heavy_candidates]

    num_capital_candidates = (total_candidates - len(heavy_candidates))
    capital_candidates = [a for (a,b) in capital_frac if a not in heavy_candidates]
    capital_candidates = capital_candidates[:num_capital_candidates]
    top_results = heavy_candidates + capital_candidates

    candidate_pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    print top_results
    for w1, w2 in candidate_pairs:
        if related([w1],[w2]):
            print w1, w2
            if cnt[w1] > cnt [w2]:
                if w2 in top_results:
                    top_results.remove(w2)
            else:
                if w1 in top_results:
                    top_results.remove(w1)
    top_results.sort(key = lambda w: -cnt[w])

    return top_results


def count_words_in_tweets(query, split_tweets, top_twitter_words):
    low_information_words = top_twitter_words
    cnt = Counter()
    capital_cnt = Counter()
    query_words = query.lower().split()
    for split_tweet in split_tweets:
        for word in split_tweet:
            if (word.lower() not in low_information_words and
            re.search("[0-9\W]",word) is None and
            related([word.lower()],query_words) is not True and
            len(word) > 2):
                cnt[word.lower()] += 1
                if len(re.findall("\A[A-Z]", word)) == 1:
                    capital_cnt[word.lower()] += 1
    keys = [key for key in cnt]
    keys.sort(key=lambda k:-cnt[k])
    return capital_cnt, cnt, keys


def related(word_list1, word_list2):
        pairs = itertools.product(word_list1, word_list2)
        for a, b in pairs:
            if (a.find(b) != -1 or b.find(a) != -1):
                 return True
        return False


def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')
