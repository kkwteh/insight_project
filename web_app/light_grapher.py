import networkx as nx
import twitter
import itertools

def compute_graph(query, top_results, tweets):
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]

    edge_threshold = 14
    for w1, w2 in pairs:
        pair_count = 0
        for tweet in tweets:
            text = tweet.lower()
            if text.count(w1) > 0 and text.count(w2) > 0:
                pair_count += 1
        if pair_count > 0 and pair_count <= 14:
            print(pair_count)
        if pair_count > edge_threshold:
            G.add_edge(w1, w2, weight=1)

    return G
