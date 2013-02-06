#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import json
from flask import Flask, render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    G = request.args.get('G')
    return render_template('graph.html', graph=G)

if '__main__' == __name__:
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
