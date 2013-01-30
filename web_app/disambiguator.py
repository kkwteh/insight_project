#!/usr/bin/env python
# coding=utf8

import grapher
import pdb
import pickle
import re
import string
import twitter
import unicodedata
from collections import Counter
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, RecaptchaField
from flask import request
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn


app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_USE_MINIFIED'] = True
app.config['BOOTSTRAP_USE_CDN'] = True
app.config['BOOTSTRAP_FONTAWESOME'] = True
app.config['SECRET_KEY'] = 'devkey'

class QueryForm(Form):
    q = TextField(' ',validators=[Required()])


@app.route('/')
def index():
    form = QueryForm()
    query = request.args.get('q')
    tweets = []
    count = {}
    keys = []
    if query is not None:
        tweets = get_tweets(query)
        count, keys = count_words_in_tweets(query, tweets)
        pickle_top_words(query, keys)
        grapher.analyze(query)

    return render_template('index.html', form=form, query=query, tweets=tweets, count=count, keys=keys, len=len(keys))


def pickle_top_words(query, keys):
    most_cooccuring = 20
    o = open("query_"+query+".pkl","wb")
    pickle.dump(keys[:most_cooccuring], o, -1)
    o.close()


def get_tweets(query):
    tweets = []
    num_pages = 16
    for i in range(1,num_pages):
        search = twitter_search.search(q=query, lang="en", page=str(i), rpp=100)
        for t in search[u'results']:
            ascii = get_ascii(t[u'text'])
            if re.search("RT",ascii) is None:
                tweets.append(ascii)
    return tweets


def init_twitter():
    CONSUMER_KEY = 'sLGccwOdfySptswo1ZKErg'
    CONSUMER_SECRET = 'z5V9g6sOJ9BEYhvsSvnzt6pjS7gVWV2komWyIz5XZE'
    oauth_token = "101769689-tPwXbgj96kaYpnCKHSijZJ5r6arePyLlMIQUj4Ts"
    oauth_secret = "ijCLoaw3bfRiOzbR572jKGQe3pYHndIps3CIp9KOWa4"
    return twitter.Twitter(domain="search.twitter.com",
                            auth=twitter.oauth.OAuth(oauth_token,
                                                oauth_secret,
                                                CONSUMER_KEY,
                                                CONSUMER_SECRET))

def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')

def count_words_in_tweets(query, tweets):
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


if '__main__' == __name__:
    twitter_search = init_twitter()
    f = open("top_twitter_words.pkl")
    top_twitter_words = pickle.load(f)
    app.run(debug=True)
