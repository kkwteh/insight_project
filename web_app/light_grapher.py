import networkx as nx
import twitter
import itertools

def compute_graph(query, top_results, tweets):
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    i = 1
    print "start edger"
    for w1, w2 in pairs:
        i += 1
        for tweet in tweets:
            text = tweet.lower()
            if text.count(w1) > 0 and text.count(w2) > 0:
                G.add_edge(w1, w2, weight=1)
                break

    print "end edger"
    return G
