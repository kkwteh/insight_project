#!/Users/teh/code/insight_project/ENV/bin/python
import tweet_slicer
import heavy_edger
import light_edger
import operator
import sys
import itertools
import json
import networkx as nx


def analyze(query, tweets, count, top_results):
    G = light_edger.compute_graph(query, top_results, tweets)
    sundry = [comp for comp in nx.connected_components(G) if len(comp) >= 2]
    cliques = []
    for comp in sundry:
        c = max(comp, key=lambda x: count[x])
        cliques.append([c])

    return cliques, jsony(G)


def jsony(G):
    nodes, edges = [], []
    for node in G.nodes():
        nodes.append({"name": node})

    for edge in G.edges():
        source, target = edge[0], edge[1]
        edges.append({"source": G.nodes().index(source),
                        "target": G.nodes().index(target)})

    jsony_G= {}
    jsony_G["nodes"] = nodes
    jsony_G["links"] = edges
    return jsony_G


def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: query'
        sys.exit(1)

    query = args[0]
    analyze(query)


if __name__ == '__main__':
    main()
