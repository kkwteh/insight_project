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
    count = count_words_in_tweets(tweets)
    return render_template('index.html', form=form, query=query, tweets=tweets, count=count, len=len(count))


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
    low_information_words = ['the', 'of', 'off', 'and', 'a', 'to', 'two', 'too', 'in', 'is', 'you', 'that', 'it', 'he', 'for', 'four', 'was', 'on', 'are', 'as', 'with', 'his', 'they', 'at', 'be', 'bee', 'this', 'from', 'i', 'eye', 'have', 'or', 'ore', 'by', 'bye', 'buy', 'one', 'won', 'had', 'not', 'knot', 'but', 'what', 'all', 'were', 'where', 'when', 'we', 'there', 'their', 'can', 'an', 'your', 'which', 'witch', 'said', 'if', 'do', 'due', 'will', 'each', 'about', 'how', 'who', 'up', 'out', 'them', 'then', 'than', 'she', 'many', 'some', 'sum', 'so', 'sew', 'these', 'would', 'wood', 'other', 'into', 'has', 'more', 'her', 'like', 'him', 'see', 'sea', 'time', 'could', 'no', 'know', 'make', 'first', 'been', 'its', 'now', 'people', 'my', 'made', 'maid', 'over', 'did', 'down', 'done', 'only', 'way', 'weigh', 'find', 'fined', 'use', 'used', 'may', 'water', 'long', 'little', 'very', 'after', 'words', 'called', 'just', 'most', 'get', 'through', 'back', 'much', 'before', 'go', 'good', 'new', 'knew', 'write', 'right', 'our', 'hour', 'me', 'man', 'men', 'woman', 'women', 'any', 'day', 'same', 'look', 'think', 'also', 'around', 'another', 'came', 'come', 'work', 'three', 'word', 'must', 'because', 'does', 'part', 'even', 'place', 'well', 'such', 'here', 'hear', 'take', 'why', 'things', 'help', 'put', 'years', 'different', 'away', 'again', 'went', 'old', 'number', 'great', 'tell', 'say', 'small', 'every', 'found', 'still', 'between', 'name', 'should', 'mr.', 'mrs.', 'ms.', 'miss', 'home', 'big', 'give', 'air', 'line', 'set', 'own', 'under', 'read', 'red', 'last', 'never', 'us', 'left', 'end', 'along', 'while', 'might', 'next', 'sound', 'below', 'saw', 'something', 'thought', 'both', 'few', 'those', 'always', 'looked', 'show', 'large', 'often', 'together', 'asked', 'house', 'world', 'going', 'want', 'fuck', 'shit', 'lol', 'hate', 'u', 'got', 'okay', 'damn', 'oh', 'yall', 'amp', "'", '-', '.', '..', '...', "'.", '--', 'love', "n't", "'s"]

    cnt = Counter()
    high_cnt = Counter()

    for tweet in tweets:
        if re.search("RT",tweet) is None:

            for punct in string.punctuation:
                safe_punct = ["'", "-", "."]
                if punct not in safe_punct:
                    tweet = tweet.replace(punct,"")

            words_of_tweet = word_tokenize(tweet)
            for word in words_of_tweet:
                cnt[word.lower()] += 1

    for key, value in cnt.iteritems():
        if value > 1 and key not in low_information_words:
            high_cnt[key] = value

    return high_cnt


if '__main__' == __name__:
    twitter_search = init_twitter()
    app.run(debug=True)
