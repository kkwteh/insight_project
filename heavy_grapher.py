import pages_getter
import params
import networkx as nx
import twitter
import itertools
import random


def compute_graph(query, top_results, tweets, lang):
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = itertools.combinations(top_results, 2)
    for w1, w2 in pairs:
        pair_count = 0
        w1_count = 0
        w2_count = 0
        for tweet in tweets:
            text = tweet.lower()
            if text.count(w1) > 0:
                w1_count += 1
            if text.count(w2) > 0:
                w2_count += 1
            if text.count(w1) > 0 and text.count(w2) > 0:
                pair_count += 1
        proportion_cooccur = 1.0*pair_count/min(w1_count,w2_count)
        if proportion_cooccur > 0.1:
            G.add_edge(w1, w2, weight=1)
    return G
