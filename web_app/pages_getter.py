#!/Users/teh/code/insight_project/ENV/bin/python
import time
import twitter
import pickle
import threading
import urllib2
import sets
import random
import cred
from Queue import Queue


def init_twitter():
    OAuth_creds = cred.twitter_OAuth
    return twitter.Twitter(domain="search.twitter.com",
                    auth=twitter.oauth.OAuth(OAuth_creds[0],
                    OAuth_creds[1],
                    OAuth_creds[2],
                    OAuth_creds[3]))


def download_page(twitter_search, query, page_num, per_page, was_seen=None):
    """ Download a page of tweets for the query"""

    if page_num != None:
        page = twitter_search.search(q=query, lang="en", page=page_num,                                             rpp=per_page)['results']

        print "Successfully downloaded page ", page_num
        return page


class TweetDownloader(threading.Thread):
    """ A class to download a user's top Artists

    To be used as an individual thread to take
    a list of users from a shared queue and
    download their top artists
    """

    def __init__(self, queue, twitter_search, was_seen=None):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.pages = []
        self.queue = queue
        self.twitter_search = twitter_search
        self.was_seen = was_seen

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

            query, page_num, per_page = self.queue.get()
            page = download_page(self.twitter_search, query, page_num,
                                            per_page, self.was_seen)
            self.pages.append((query,page))
            print "Successfully processed page_num: ", page_num,
            print " by thread: ", self.ident


def get_pages_of_tweets(twitter_search, query, page_nums, per_page, num_threads=None, lite=False):
    if num_threads is None:
        num_threads = len(query)
    """ Download 'num_pages' pages from Twitter api.
    These documents are downloaded in parallel using
    separate threads

    """
    if lite == True:
        was_seen = seer()
    else:
        was_seen = None
    q = Queue()
    threads = []

    for i in xrange(num_threads):
        thread = TweetDownloader(q, twitter_search, was_seen)
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)

    for i in xrange(len(query)):
        q.put((query[i], page_nums[i], per_page))

    while not q.empty():
        time.sleep(1.0)

    for thread in threads:
        thread.stop()
    for thread in threads:
        thread.join()

    pages = []
    for thread in threads:
        pages.extend(thread.get_pages())

    return pages


def seer():
    the_list = set()
    def f(word):
        if word in the_list:
            return True
        else:
            the_list.add(word)
            return False
    return f
