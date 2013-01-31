#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import grapher
import tweet_slicer
import recommender
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
    recommendations = []
    if query is not None:
        query = tweet_slicer.get_ascii(query.lower())
        tweets, count, keys = tweet_slicer.slice_up(query)
        cliques = grapher.analyze(query, tweets)
        recommendations = recommender.find(query, cliques)

    return render_template('index.html', form=form, query=query, tweets=tweets, count=count, keys=keys, len=len(keys), recommendations=recommendations)

if '__main__' == __name__:
    app.run(debug=True)
