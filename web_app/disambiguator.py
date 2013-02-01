#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import grapher
import tweet_slicer
import recommender
import json
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
    (jsonG, count, tweets, keys, cliques, recommendations, G) = (None, {} ,
                             [],[],[],[],[])

    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        tweets, count, keys, top_results = tweet_slicer.slice_up(query)
        cliques, G = grapher.analyze(query, tweets, top_results)
        jsonG = json.dumps(G)
        recommendations = recommender.find(query, cliques)


    return render_template('index.html', form=form, query=query, tweets=tweets,
                            count=count, keys=keys, len=len(keys),
                            recommendations=recommendations, graph=jsonG)

@app.route('/graph')
def graph():
    G = json.loads(request.args.get('G'))
    vertices = G[0]
    edges = G[1]
    return render_template('graph.html', vertices=vertices, edges=edges)

if '__main__' == __name__:
    app.run(debug=True)
