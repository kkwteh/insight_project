#!/Users/teh/code/insight_project/ENV/bin/python
import pickle
import re
import string
import twitter
import unicodedata
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

def init_data():
    f = open("top_twitter_words.pkl")
    top_twitter_words = pickle.load(f)
    return top_twitter_words


def slice_up(twitter_search, query):
    top_twitter_words = init_data()
    tweets = get_tweets(twitter_search, query)
    count, keys = count_words_in_tweets(query, tweets, top_twitter_words)
    pickle_top_words(query, keys)
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
    return tweets


def count_words_in_tweets(query, tweets):
    pass


def pickle_top_words(query, keys):
    most_cooccuring = 20
    o = open("query_"+query+".pkl","wb")
    pickle.dump(keys[:most_cooccuring], o, -1)
    o.close()


def count_words_in_tweets(query, tweets, top_twitter_words):
    common_many_words = 5000
    pairs = top_twitter_words[:common_many_words]
    low_information_words = [x[0] for x in pairs]
    cnt = Counter()
    high_cnt = Counter()

    for tweet in tweets:
        clean_punct(tweet)
        tweet = disguise_hash_marks(tweet)   #avoid quirk of word_tokenize
        words_of_tweet = word_tokenize(tweet)

        for word in words_of_tweet:

            word = replace_hash_marks(word)

            #remove all punctuation from front and back of string
            word = re.sub("\A['-.]*", "", word)
            word = re.sub("['-.]*\Z", "", word)

            #store words that are a) not low information words and do not
            #contain numbers and are not the query itself and
            #b) wn knows about or begin with a single
            #capital letter
            if (word.lower() not in low_information_words and
                re.search("[0-9]",word) is None and
                word.lower() != query):
                if wn.synsets(word.lower()) != []:
                    cnt[word.lower()] += 1
                elif re.search("\A[A-Z][^A-Z]*\Z",word) is not None:
                    cnt[word] += 1
    keys = [key for key in cnt if cnt[key] >= 2]
    keys.sort(key=lambda k:-cnt[k])
    return cnt, keys


def disguise_hash_marks(tweet):
    return tweet.replace("#","~")


def replace_hash_marks(word):
    return word.replace("~","#")


def clean_punct(tweet):
    safe_punct = ["'", "-", ".", "#"]
    for punct in string.punctuation:
        if punct not in safe_punct:
            tweet = tweet.replace(punct,"")


def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')
