#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import clusterer
import tweet_slicer
import recommender
import json
import sys
import os
from flask import Flask, render_template
from flask import request

is_lite = None
app = Flask(__name__)


@app.route('/search')
def search():
    query = request.args.get('q')
    (count, tweet_ids, tweets, keys, cliques, recommendations, G) = ({} ,[],
                             [], [], [], [], None)
    if query == u'':
        return render_template('index.html')
    else:
        query = tweet_slicer.get_ascii(query.lower())
        num_results = 20
        tweets, count, keys, top_results = tweet_slicer.slice_up(query,
                                                    num_results)
        tweets_text = [t['text'] for t in tweets]
        cliques, G = clusterer.analyze(is_lite, query, tweets_text, count, top_results)
        recommendations = recommender.find(tweets, cliques)

    return render_template('search.html', query=query, tweet_ids=tweet_ids,
                            count=count, keys=keys, len=len(keys),
                            recommendations=recommendations, graph=G)

@app.route('/refine')
def refine():
    query = request.args.get('q')
    page = request.args.get('page')
    query = tweet_slicer.get_ascii(query.lower())
    tweets = tweet_slicer.simple_get(query)
    filter = request.args.get('filter')
    if filter != "'":
        filter_words = filter.split()
        filtered_tweets = []
        for tweet in tweets:
            for word in filter_words:
                if tweet['text'].lower().find(word) >= 0:
                    filtered_tweets.append(tweet)
                    break
        tweets = filtered_tweets
    tweets_per_page = 15
    tweet_ids = [t['id'] for t in tweets][:tweets_per_page]
    return render_template('refine.html', query=query, tweet_ids=tweet_ids, filter=filter)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    G = request.args.get('G')
    return render_template('graph.html', graph=G)

@app.route('/about')
def about():
    return render_template('about.html')

if '__main__' == __name__:
    args = sys.argv[1:]
    if not args:
        debug = False
    elif args[0] == '--debug':
        debug = True
    else:
        print 'usage: [--debug]'
        sys.exit(1)

    if debug == False:
        port = int(os.environ.get('PORT', 5000))
        app.run(host="0.0.0.0", port=port)
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
