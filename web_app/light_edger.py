import networkx as nx
import twitter
import itertools

def compute_graph(query, top_results, tweets):
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    i = 1
    for w1, w2 in pairs:
        print "pair {}/{}".format(i,len(pairs))
        i += 1
        for tweet in tweets:
            if tweet.count(w1) > 0 and tweet.count(w2) > 0:
                G.add_edge(w1, w2, weight=1)
                print("edge")
                break

    for node in G.nodes():
        if G.degree(node) > 1000:
            G.remove_node(node)
    return G
