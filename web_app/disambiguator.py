#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import clusterer
import tweet_slicer
import recommender
import json
import sys
from flask import Flask, render_template
from flask import request

is_lite = None
app = Flask(__name__)


@app.route('/')
def index():
    query = request.args.get('q')
    filter = request.args.get('filter')
    if filter is None:
        wants_recs = True
        filter = ""
    else:
        filter_words = filter.split()
        wants_recs = False

    (count, tweet_ids, tweets, keys, cliques, recommendations, G) = ({} ,[],
                             [], [], [], [], None)

    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        if is_lite:
            num_results = 30
        else:
            num_results = 13
        tweets, count, keys, top_results = tweet_slicer.slice_up(query,
                                                            num_results)
        if wants_recs:
            tweets_text = [t['text'] for t in tweets]
            cliques, G = clusterer.analyze(is_lite, query, tweets_text, count, top_results)
            recommendations = recommender.find(tweets, cliques)

        if filter != "":
            filtered_tweets = []
            for tweet in tweets:
                for word in filter_words:
                    if tweet['text'].lower().find(word) >= 0:
                        filtered_tweets.append(tweet)
                        break
            tweets = filtered_tweets

        to_display = 30
        tweet_ids = [t['id'] for t in tweets][:to_display]
    return render_template('index.html', query=query, tweet_ids=tweet_ids,
                            count=count, keys=keys, len=len(keys),
                            recommendations=recommendations, graph=G,
                            filter=filter)

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

    app.run(host="0.0.0.0", port=5001, debug=True)
