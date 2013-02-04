#!/Users/teh/code/insight_project/ENV/bin/python
import time
import twitter
import pickle
import threading
import urllib2
from Queue import Queue

def init_twitter():
    f = open("twitter_oauth.pkl")
    cred = pickle.load(f)
    return twitter.Twitter(domain="search.twitter.com",
                    auth=twitter.oauth.OAuth(cred[0],cred[1],cred[2],cred[3]))

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
