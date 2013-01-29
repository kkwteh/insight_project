#!/usr/bin/env python
# coding=utf8
import twitter
import unicodedata

from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, RecaptchaField
from flask import request

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
    return render_template('index.html', form=form, query=query, tweets=tweets)


def get_tweets(query):
    search = twitter_search.search(q=query, lang="en", count="100")
    return [get_ascii(t[u'text']) for t in search[u'results']]


def init_twitter():
    return twitter.Twitter(domain="search.twitter.com")

def get_ascii(u_string):
    return unicodedata.normalize('NFKD', u_string).encode('ascii','ignore')

if '__main__' == __name__:
    twitter_search = init_twitter()
    app.run(debug=True)

