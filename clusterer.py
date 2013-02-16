#!/Users/teh/code/insight_project/ENV/bin/python
import params
import tweet_slicer
import heavy_grapher
import operator
import sys
import itertools
import json
import networkx as nx
import sets

def get_nodes_seen(sundry):
    if len(sundry) >= 2:
        nodes_seen = reduce(lambda x, y : set(x).union(set(y)), sundry)
    elif len(sundry) == 1:
        nodes_seen = set(sundry[0])
    else:
        nodes_seen = set()
    return nodes_seen


def heavy_clusters(G, count, top_results):
    comps = nx.connected_components(G)
    sundry = [comp for comp in comps if len(comp) >= 2]
    sundry.sort(key= lambda clique: -len(clique))
    nodes_seen = get_nodes_seen(sundry)

    total_words = sum([count[key] for key in count])
    heavy = params.candidate_is_heavy_factor
    singles = [[key] for key in count if (count[key] >= heavy*total_words
                                            and key not in nodes_seen)]
    sundry.extend(singles)
    sundry.sort(key= lambda clique: -total_weight(clique, count))
    cols = params.number_clusters_on_page
    hot_sets = sundry[:cols]
    return hot_sets


def total_weight(clique,count):
    print clique, ": clique weight"
    print sum([count[w] for w in clique])
    return sum([count[w] for w in clique])


def analyze(query, tweets, count, top_results):
    G = heavy_grapher.compute_graph(query, top_results, tweets)
    hot_sets = heavy_clusters(G, count, top_results)
    return hot_sets, jsony(G, count)


def jsony(G, count):
    nodes, edges = [], []
    for node in G.nodes():
        nodes.append({"name": "{}".format(node)})

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
