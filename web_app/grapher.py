#!/Users/teh/code/insight_project/ENV/bin/python
import tweet_slicer
import heavy_edger
import light_edger
import operator
import sys
import itertools
import json
import networkx as nx
import sets

def analyze(query, tweets, count, top_results):
    G = heavy_edger.compute_graph(query, top_results, tweets)
    gen = nx.find_cliques(G)
    sundry = [clique for clique in gen if len(clique) >= 2]
    sundry.sort(key= lambda clique: -len(clique))

    nodes_seen = set()
    for clique in sundry[:]:
        if len(nodes_seen.intersection(set(clique))) > 0:
            sundry.remove(clique)
        else:
            nodes_seen = nodes_seen.union(clique)

    total_words = sum([count[key] for key in count])
    preface = [[key] for key in count if (count[key] >= 0.04*total_words
                                            and key not in nodes_seen)]
    preface.extend(sundry)
    hot_sets = preface[:3]
    return hot_sets, jsony(G, count)


def jsony(G, count):
    nodes, edges = [], []
    for node in G.nodes():
        nodes.append({"name": "{}: {}".format(node, count[node])})

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
