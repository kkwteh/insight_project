#!/Users/teh/code/insight_project/ENV/bin/python
import params
import cred
import time
import twitter
import pickle
import threading
import urllib2
import sets
import random
from Queue import Queue


def init_twitter():
    OAuth_creds = cred.twitter_OAuth
    return twitter.Twitter(domain="search.twitter.com",
                    auth=twitter.oauth.OAuth(OAuth_creds[0],
                    OAuth_creds[1],
                    OAuth_creds[2],
                    OAuth_creds[3]))


def download_page(twitter_search, query, page_num, per_page):
    if page_num != None:
        page = twitter_search.search(q=query, lang="en", page=page_num,                                             rpp=per_page)['results']

        print "Successfully downloaded page ", page_num
        return page


class TweetDownloader(threading.Thread):
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

            query, page_num, per_page = self.queue.get()
            page = download_page(self.twitter_search, query, page_num,
                                            per_page)
            self.pages.append((query,page))
            print "Successfully processed page_num: ", page_num,
            print " by thread: ", self.ident


def get_pages_of_tweets(twitter_search, query, page_nums, per_page):
    num_threads=len(query)
    q = Queue()
    threads = []

    for i in xrange(num_threads):
        thread = TweetDownloader(q, twitter_search)
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
