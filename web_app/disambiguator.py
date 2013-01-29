#!/usr/bin/env python
# coding=utf8

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
    tweets = get_tweets(query)
    count, keys = count_words_in_tweets(tweets)
    return render_template('index.html', form=form, query=query, tweets=tweets, count=count, keys=keys, len=len(count))


def get_tweets(query):
    tweets = []
    num_pages = 16
    for i in range(1,num_pages):
        search = twitter_search.search(q=query, lang="en", page=str(i))
        tweets.extend([get_ascii(t[u'text']) for t in search[u'results']])
    return tweets


def init_twitter():
    return twitter.Twitter(domain="search.twitter.com")

def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')

def count_words_in_tweets(tweets):
    common_many_words = 200
    low_information_words = top_5000[:common_many_words]
    low_information_words.extend(['fuck', 'shit', 'lol', 'hate', 'u', 'got', 'okay', 'damn', 'oh', 'yall', 'amp', "'", '-', '.', '..', '...', "'.", '--', 'love', "n't", "'s", "'re", "'ve"])
    cnt = Counter()
    high_cnt = Counter()

    for tweet in tweets:
        if re.search("RT",tweet) is None:

            clean_punct(tweet)
            tweet = disguise_hash_marks(tweet)   #avoid quirk of word_tokenize
            words_of_tweet = word_tokenize(tweet)

            for word in words_of_tweet:

                word = replace_hash_marks(word)

                #remove all punctuation from front and back of string
                word = re.sub("\A['-.]*", "", word)
                word = re.sub("['-.]*\Z", "", word)

                #store words that wn knows about or begin with a single capital
                #letter
                if (wn.synsets(word.lower()) != [] and
                word.lower() not in low_information_words):
                    cnt[word.lower()] += 1
                elif (wn.synsets(word.lower()) == [] and
                    re.search("\A[A-Z][^A-Z]*\Z",word) is not None):
                    cnt[word] += 1
                elif re.search("\A#",word) is not None:
                    cnt[word.lower()] += 1
    keys = cnt.keys()
    keys.sort()
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
    f = open("top_5000.pkl")
    top_5000 = pickle.load(f)
    app.run(debug=True)
