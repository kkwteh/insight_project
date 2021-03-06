#!/Users/teh/code/insight_project/ENV/bin/python
import pages_getter
import top_words_data
import params
import sys
import itertools
import time
import twitter
import pickle
import re
import os
import string
import sets
import unicodedata
import threading
import urllib2
from Queue import Queue
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer


def init_data(lang):
    if lang == "en":
        top_pairs = top_words_data.pairs
    elif lang == "es":
        top_pairs = top_words_data.es_pairs
    top_words = [pair[0] for pair in top_pairs]
    return top_words


def simple_get(query, lang):
    twitter_search = pages_getter.init_twitter()
    num_pages = 15
    per_page = 100
    query_list = [query for i in range(num_pages)]
    page_nums = [i + 1 for i in range(num_pages)]
    pages_with_queries = pages_getter.get_pages_of_tweets(twitter_search,
                                                            query_list,
                                                            page_nums,
                                                            per_page,
                                                            lang)
    pages = [pair[1] for pair in pages_with_queries]
    tweets = flatten(pages)
    return tweets


def slice_up(query, lang):
    query = query.lower()
    num_results = params.number_candidates_considered
    top_twitter_words = init_data(lang)
    tweets = simple_get(query, lang)
    split_tweets = clean_tweets(query, tweets)
    capital_count, count, keys = count_words_in_tweets(query,
                                                split_tweets,
                                                top_twitter_words)
    top_results = extract_top_results(query,
                                num_results,
                                capital_count,
                                count,
                                keys)
    return tweets, count, keys, top_results


def flatten(pages):
    return list(itertools.chain.from_iterable(pages))


def clean_tweets(query, tweets):
    split_tweets = sets.Set()
    query_words = query.split()
    tweets = uniq_on_id(tweets)
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

def uniq_on_id(tweets):
    ids_seen = []
    uniq_ids_tweets = []
    for tweet in tweets:
        if tweet['from_user_id'] not in ids_seen:
            ids_seen.append(tweet['from_user_id'])
            uniq_ids_tweets.append(tweet)
    return uniq_ids_tweets

def extract_top_results(query, num_results, capital_cnt, cnt, keys):
    cap_freq = params.capitalization_frequency_cutoff
    prop_heavy = params.proportion_of_heavy_candidates

    capital_frac = [(key, capital_cnt[key] * 1.0 / cnt[key]) for key in
                                                    capital_cnt if cnt[key] > 1]
    capital_frac = [(a,b) for (a,b) in capital_frac if cap_freq <= b]
    capital_frac.sort(key= lambda (a,b): -cnt[a])

    just_counts = [cnt[key] for key in keys]

    total_candidates = num_results
    max_heavy_candidates = int(prop_heavy * total_candidates)
    heavy_factor = params.counts_as_heavy_factor

    heavy_candidates = [key for key in cnt if (cnt[key] > heavy_factor *
                                                sum(just_counts))]
    heavy_candidates.sort(key= lambda w: -cnt[w])
    heavy_candidates = heavy_candidates[:max_heavy_candidates]

    num_capital_candidates = (total_candidates - len(heavy_candidates))
    capital_candidates = [a for (a,b) in capital_frac if a not in
                                                        heavy_candidates]
    capital_candidates = capital_candidates[:num_capital_candidates]
    top_results = heavy_candidates + capital_candidates

    candidate_pairs = [(x,y) for (x,y) in itertools.product(top_results,
                                                        repeat = 2) if x < y ]
    for w1, w2 in candidate_pairs:
        if have_common_stems(w1,w2):
            descending_pair = sorted([w1,w2], key= lambda w: -cnt[w])
            top_results, cnt = consolidate (descending_pair, top_results, cnt)

    top_results.sort(key = lambda w: -cnt[w])
    return top_results


def consolidate (descending_pair, top_results, count):
    high, low = descending_pair
    if high not in top_results or low not in top_results:
        return top_results, count
    else:
        count[high] += count[low]
        del count[low]
        top_results.remove(low)
        return top_results, count


def count_words_in_tweets(query, split_tweets, top_twitter_words):
    low_information_words = top_twitter_words
    cnt = Counter()
    capital_cnt = Counter()
    query_words = query.lower().split()
    min_len = params.minimum_word_length
    for split_tweet in split_tweets:
        for word in split_tweet:
            if (word.lower() not in low_information_words and
            re.search("[0-9\W]",word) is None and
            related([word.lower()],query_words) is not True and
            len(word) >= min_len):
                cnt[word.lower()] += 1
                if len(re.findall("\A[A-Z]", word)) == 1:
                    capital_cnt[word.lower()] += 1
    keys = [key for key in cnt]
    keys.sort(key=lambda k:-cnt[k])
    return capital_cnt, cnt, keys


def have_common_stems(word1, word2):
    stemmer = PorterStemmer()
    if (stemmer.stem(word1) == stemmer.stem(word2)):
        return True
    else:
        return False


def related(word_list1, word_list2):
    pairs = itertools.product(word_list1, word_list2)
    for a, b in pairs:
        if (a.find(b) != -1 or b.find(a) != -1):
             return True
    return False
