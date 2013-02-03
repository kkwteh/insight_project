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
from Queue import Queue
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

def init_data():
    f = open("top_twitter_words.pkl")
    top_pairs= pickle.load(f)
    top_words = [pair[0] for pair in top_pairs]
    top_words.extend(["w"])
    return top_words


def init_twitter():
    f = open("twitter_oauth.pkl")
    cred = pickle.load(f)
    return twitter.Twitter(domain="search.twitter.com",
                    auth=twitter.oauth.OAuth(cred[0],cred[1],cred[2],cred[3]))


def slice_up(query):
    twitter_search = init_twitter()
    top_twitter_words = init_data()

    num_pages = 15
    per_page = 100
    query_list = [query for i in range(num_pages)]
    page_nums = [i + 1 for i in range(num_pages)]
    pages_with_queries = get_pages_of_tweets(twitter_search, query_list, page_nums, per_page)
    pages = [pair[1] for pair in pages_with_queries]
    print "finished download"
    full_tweets = flatten(pages)
    print "flattened pages"
    tweets = [get_ascii(t[u'text']) for t in full_tweets]
    print "got tweets"
    split_tweets = clean_tweets(tweets)
    print "cleaned tweets"
    count, keys = count_words_in_tweets(query, split_tweets, top_twitter_words)
    print "counted words"
    top_results = extract_top_results(query, count, keys)
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
        tweet = clean_punct(tweet)
        split_tweets.add(tuple(word_tokenize(tweet)))

    for split_tweet in split_tweets:
        for word in split_tweet:
            word = re.sub("\A['-\.]*", "", word)
            word = re.sub("['-\.]*\Z", "", word)
    return list(split_tweets)


def extract_top_results(query, count, keys):
    just_counts = [count[key] for key in keys]
    a = np.array(just_counts)
    max_candidates = 30
    percentile = 100 * max(1 - (1.0 * max_candidates)/len(a),0)
    min((1.0 * max_candidates)/len(a),100)
    top_results = [key for key in keys if count[key] > np.percentile(a, percentile)]
    return top_results


def count_words_in_tweets(query, split_tweets, top_twitter_words):
    low_information_words = top_twitter_words
    cnt = Counter()

    for split_tweet in split_tweets:
        for word in split_tweet:
            #store all words not in low_information words
            if (word.lower() not in low_information_words and
                re.search("[0-9]",word) is None and
                related(word.lower(),query.lower()) is not True):
                cnt[word.lower()] += 1
    keys = [key for key in cnt]
    keys.sort(key=lambda k:-cnt[k])
    return cnt, keys

def related(word1, word2):
        if (re.search(word1, word2) is None and
             re.search(word2, word1) is None):
            return False
        else:
            return True


def clean_punct(tweet):
    for punct in string.punctuation:
        tweet = tweet.replace(punct,"")
    return tweet


def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')




def download_page(twitter_search, query, page_num, per_page):
    """ Download a page of tweets for the query"""
    try:
        if page_num != None:
            page = twitter_search.search(q=query, lang="en", page=page_num,                                             rpp=per_page)['results']
            print "Successfully downloaded page ", page_num
            return page
    except urllib2.HTTPError, e:
        print e.code
        print "Failed to get page"
        return None

class TweetDownloader(threading.Thread):
    """ A class to download a user's top Artists

    To be used as an individual thread to take
    a list of users from a shared queue and
    download their top artists
    """

    def __init__(self, queue, twitter_search):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.pages = []
        self.queue = queue
        self.twitter_search = twitter_search

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def get_pages(self):
        return self.pages

    def run(self):
        while True:
            if self.stopped():
                return
            if self.queue.empty():
                time.sleep(0.1)
                continue
            try:
                query, page_num, per_page = self.queue.get()
                page = download_page(self.twitter_search, query, page_num,
                                                per_page)
                self.pages.append((query,page))
                print "Successfully processed page_num: ", page_num,
                print " by thread: ", self.ident
                # No need for a 'queue.task_done' since we're
                # not joining on the queue
            except:
                print "Failed to process page_num: ", page_num
                raise

#query is an array of queries
#page_nums is an array of page numbers
def get_pages_of_tweets(twitter_search, query, page_nums, per_page, num_threads=None):
    if num_threads is None:
        num_threads = len(query)
    """ Download 'num_pages' pages from Twitter api.
    These documents are downloaded in parallel using
    separate threads

    """

    q = Queue()
    threads = []

    try:
        # Create the threads and 'start' them.
        # At this point, they are listening to the
        # queue, waiting to consume

        for i in xrange(num_threads):
            thread = TweetDownloader(q, twitter_search)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        # We want to download one array for each page number,
        # so we put every page number in the queue, and
        # these will be processed by the threads
        for i in xrange(len(query)):
            q.put((query[i], page_nums[i], per_page))

        # Wait for all entries in the queue
        # to be processed by our threads
        # One could do a queue.join() here,
        # but I prefer to use a loop and a timeout
        while not q.empty():
            time.sleep(1.0)

        # Terminate the threads once our
        # queue has been fully processed
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()

    except:
        print "Main thread hit exception"
        # Kill any running threads
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()
        raise

    # Collect all downloaded documents
    # from our threads
    pages = []
    for thread in threads:
        pages.extend(thread.get_pages())

    return pages
