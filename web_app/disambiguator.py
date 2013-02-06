#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import clusterer
import tweet_slicer
import recommender
import json
from flask import Flask, render_template
from flask import request

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
        tweets, count, keys, top_results = tweet_slicer.slice_up(query)
        if wants_recs:
            tweets_text = [t['text'] for t in tweets]
            cliques, G = clusterer.analyze(query, tweets_text, count, top_results)
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
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
