#!/usr/bin/env python
# coding=utf8

import grapher
import tweet_slicer
import twitter
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
    tweets = []
    count = {}
    keys = []
    if query is not None:
        tweets, count, keys = tweet_slicer.slice_up(twitter_search, query)
        grapher.analyze(query)

    return render_template('index.html', form=form, query=query, tweets=tweets, count=count, keys=keys, len=len(keys))


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


if '__main__' == __name__:
    twitter_search = init_twitter()
    app.run(debug=True)
