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
    if query is None:
        return render_template('index.html')
    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        if is_lite:
            num_results = 30
        else:
            num_results = 15
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
    query = tweet_slicer.get_ascii(query.lower())
    num_results = 15
    tweets, _, _, _ = tweet_slicer.slice_up(query, num_results)

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

    to_display = 30
    tweet_ids = [t['id'] for t in tweets][:to_display]
    return render_template('refine.html', query=query, tweet_ids=tweet_ids, filter=filter)

##mode variable controls flow of index page
##"recs" shows three columns of recommendations
##"all" shows one column of all tweets
##"filter" shows one column of filtered tweets
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    G = request.args.get('G')
    return render_template('graph.html', graph=G)

if '__main__' == __name__:
    args = sys.argv[1:]

    if not args:
        is_lite = False
    elif args[0] == '--lite':
        is_lite = True
    else:
        print 'usage: [--lite]'
        sys.exit(1)

    # app.run(host="0.0.0.0", port=5001, debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
