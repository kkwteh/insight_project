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

    if request.args.get('recs') == "False":
        wants_recs = False
    else:
        wants_recs = True

    (count, tweets, keys, cliques, recommendations, G) = ({} ,
                             [], [], [], [], None)

    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        try:
            tweets, count, keys, top_results = tweet_slicer.slice_up(query)
        except:
            return render_template('index.html')
        if wants_recs:
            cliques, G = grapher.analyze(query, tweets, count, top_results)
            recommendations = recommender.find(tweets, cliques)
            recommendations = recommendations[:3]

    return render_template('index.html', query=query, tweets=tweets,
                            count=count, keys=keys, len=len(keys),
                            recommendations=recommendations, graph=G)

@app.route('/graph')
def graph():
    G = request.args.get('G')
    return render_template('graph.html', graph=G)

if '__main__' == __name__:
    app.run(debug=True)
    #app.run(host="192.168.1.8", port=8000, debug=True)

