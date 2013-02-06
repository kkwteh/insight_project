#!/Users/teh/code/insight_project/ENV/bin/python
import tweet_slicer
import heavy_grapher
import light_grapher
import operator
import sys
import itertools
import json
import networkx as nx
import sets

def heavy_clusters(G, count, top_results):
    comps = nx.connected_components(G)
    sundry = [comp for comp in comps if len(comp) >= 2]
    sundry.sort(key= lambda clique: -len(clique))
    if len(sundry) >= 2:
        nodes_seen = reduce(lambda x, y : set(x).union(set(y)), sundry)
    elif len(sundry) == 1:
        nodes_seen = set(sundry[0])
    else:
        nodes_seen = set()

    total_words = sum([count[key] for key in count])
    super_heavy = 0.04
    preface = [[key] for key in count if (count[key] >= super_heavy*total_words
                                            and key not in nodes_seen)]
    preface.extend(sundry)

    chosen_ones = []
    for group in preface:
        for word in group:
            chosen_ones.append(word)

    kinda_heavy = 0.01
    left_overs = [[word] for word in top_results if (word not in chosen_ones
                                    and count[word] >= kinda_heavy*total_words)]
    left_overs.sort(key= lambda x : -count[x[0]])
    filler_length = 3 - len(preface)
    preface.extend(left_overs[:filler_length])

    hot_sets = preface[:3]
    return hot_sets

def max_weight(clique,count):
    print clique, ": clique weight"
    print sum([count[w] for w in clique])
    return sum([count[w] for w in clique])

def lite_clusters(G, count, top_results):
    gen = nx.find_cliques(G)
    sundry = [set(clique) for clique in gen if len(clique) >= 2]
    sundry.sort(key= lambda clique: -max_weight(clique, count))

    nodes_seen = set()
    for index, clique in enumerate(sundry[:]):
        print "before"
        print sundry[index]
        sundry[index] = sundry[index].difference(nodes_seen)
        print "after"
        print sundry[index]
        nodes_seen = nodes_seen.union(clique)

    sundry.sort(key= lambda clique: -max_weight(clique, count))

    total_words = sum([count[key] for key in count])
    preface = [[key] for key in count if (count[key] >= 0.04*total_words
                                            and key not in nodes_seen)]
    preface.extend(sundry)

    chosen_ones = []
    for group in preface:
        for word in group:
            chosen_ones.append(word)

    kinda_heavy = 0.01
    left_overs = [[word] for word in top_results if (word not in chosen_ones
                                    and count[word] >= kinda_heavy*total_words)]
    left_overs.sort(key= lambda x : -count[x[0]])
    filler_length = 3 - len(preface)
    preface.extend(left_overs[:filler_length])

    hot_sets = preface[:3]
    return hot_sets



def analyze(is_lite, query, tweets, count, top_results):
    if is_lite:
        G = light_grapher.compute_graph(query, top_results, tweets)
    else:
        G = heavy_grapher.compute_graph(query, top_results, tweets)

    if is_lite:
        hot_sets = lite_clusters(G, count, top_results)
    else:
        hot_sets = heavy_clusters(G, count, top_results)

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
