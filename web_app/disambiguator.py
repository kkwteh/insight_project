#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import grapher
import tweet_slicer
import recommender
import json
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask import request

app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_USE_MINIFIED'] = True
app.config['BOOTSTRAP_USE_CDN'] = True
app.config['BOOTSTRAP_FONTAWESOME'] = True
app.config['SECRET_KEY'] = 'devkey'


@app.route('/')
def index():
    query = request.args.get('q')

    filter = request.args.get('filter')
    if filter is None:
        wants_recs = True
    else:
        filter = filter.split()
        wants_recs = False

    (count, tweets, keys, cliques, recommendations, G) = ({} ,
                             [], [], [], [], None)

    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        tweets, count, keys, top_results = tweet_slicer.slice_up(query)
        if wants_recs:
            cliques, G = grapher.analyze(query, tweets, count, top_results)
            recommendations = recommender.find(tweets, cliques)
            recommendations = recommendations[:3]

        if filter is not None:
            filtered_tweets = []
            for tweet in tweets:
                for word in filter:
                    if tweet.lower().find(word) >= 0:
                        filtered_tweets.append(tweet)
                        break
            tweets = filtered_tweets

    return render_template('index.html', query=query, tweets=tweets,
                            count=count, keys=keys, len=len(keys),
                            recommendations=recommendations, graph=G)

@app.route('/graph')
def graph():
    G = request.args.get('G')
    return render_template('graph.html', graph=G)

if '__main__' == __name__:
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
