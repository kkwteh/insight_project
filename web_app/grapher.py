#!/Users/teh/code/insight_project/ENV/bin/python
import tweet_slicer
import heavy_edger
import light_edger
import pickle
import sys
import os
import itertools
import networkx as nx


def pickle_data(data, o_name):
    g = open(o_name, "wb")
    pickle.dump(data, g, -1)


def analyze(query, tweets, top_results):
    G = light_edger.compute_graph(query, top_results, tweets)
    pickle_data(G, "graph_" + query + ".pkl")
    sundry = [comp for comp in nx.connected_components(G) if len(comp) >= 2]
    cliques = []
    for comp in sundry:
        g = nx.find_cliques(G.subgraph(comp))
        c = g.next()[:3]
        cliques.append(c)
    return cliques, [G.nodes(), G.edges()]

def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: query'
        sys.exit(1)

    query = args[0]
    analyze(query)

if __name__ == '__main__':
    main()
