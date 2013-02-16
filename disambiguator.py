#!/Users/teh/code/insight_project/ENV/bin/python
# coding=utf8

import clusterer
import tweet_slicer
import sim_data.c_sharp
import sim_data.python
import params
import recommender
import json
import sys
import os
import re
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q')
    try:
        if sim == True:
            (sim_query,
            preview_ids,
            clique_strings,
            G,
            cluster_ids_all,
            all_ids) = get_my_sim_data(query)
            return render_template('search.html',
                                query= sim_query,
                                recommendations= preview_ids,
                                cliques= clique_strings,
                                graph= G,
                                clusters_all= cluster_ids_all,
                                all_ids= all_ids)
    except NameError:
        #sim not defined, which means app was run with gunicorn continue with
        #full application
        pass

    if query == u'':
        return render_template('index.html')
    else:
        tweets, count, keys, top_results = tweet_slicer.slice_up(query)
        ids_kept = params.ids_kept_per_cluster
        all_ids = [t['id'] for t in tweets][:ids_kept]
        tweets_text = [t['text'] for t in tweets]
        cliques, G = clusterer.analyze(query, tweets_text, count, top_results)
        cluster_ids_all, clique_strings = recommender.find(tweets, cliques)
        cluster_ids_all = [col[:ids_kept] for col in cluster_ids_all]
        preview_length = params.preview_column_length
        preview_ids = [column[:preview_length] for column in cluster_ids_all]

    print clique_strings
    return render_template('search.html',
                            query= query,
                            count= count,
                            keys= keys,
                            len= len(keys),
                            recommendations= preview_ids,
                            cliques= clique_strings,
                            graph= G,
                            clusters_all= cluster_ids_all,
                            all_ids= all_ids)


@app.route('/refine')
def refine():
    query = request.args.get('q')
    page_number = int(request.args.get('page'))
    clique = request.args.get('filter')
    ids_string = request.args.get('ids')
    clique_ids = parse_ints(ids_string)

    tweets_per_page = params.tweets_per_page

    next_page_number = get_next_number(clique_ids, page_number, tweets_per_page)
    page_ids = tweet_ids_page(clique_ids, page_number, tweets_per_page)
    return render_template('refine.html', query=query,
                                        page_ids=page_ids,
                                        filter=clique,
                                        next_page=next_page_number,
                                        ids=ids_string)


def parse_ints(ids_string):
    return re.sub("[\[\],]","", ids_string).split()


def tweet_ids_page(clique_ids, page_number, tweets_per_page):
    if page_number == -1:
        raise
    else:
        n = page_number
        pp = tweets_per_page
        return [id_num for id_num in clique_ids[pp*(n - 1):pp*n]]


def get_next_number(clique_ids, page_number, tweets_per_page):
    if len(clique_ids) > tweets_per_page * page_number:
        return page_number + 1
    else:
        return -1


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



def get_my_sim_data(query):
    if query == 'python':
        return (sim_data.python.query,
                    sim_data.python.preview_ids,
                    sim_data.python.clique_strings,
                    sim_data.python.G,
                    sim_data.python.cluster_ids_all,
                    sim_data.python.all_ids)
    else:
        return (sim_data.c_sharp.query,
                    sim_data.c_sharp.preview_ids,
                    sim_data.c_sharp.clique_strings,
                    sim_data.c_sharp.G,
                    sim_data.c_sharp.cluster_ids_all,
                    sim_data.c_sharp.all_ids)

if '__main__' == __name__:
    args = sys.argv[1:]
    debug = False
    sim = False
    if not args:
        pass
    elif args[0] == '--debug':
        debug = True
    elif args[0] == '--sim':
        sim = True
        debug = True
    else:
        print 'usage: [--debug, --fake]'
        sys.exit(1)

    if debug == False:
        port = int(os.environ.get('PORT', 5000))
        app.run(host="0.0.0.0", port=port)
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
