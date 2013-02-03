import tweet_slicer
import networkx as nx
import twitter
import itertools

def compute_graph(query, top_results, tweets):
    searcher = tweet_slicer.init_twitter()
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    i = 0
    for w1, w2 in pairs:
        triple = query + " " + w1 + " " + w2
        s = searcher.search(q=triple, lang="en")
        print i
        i += 1
        print len(s[u'results'])
        if len(s[u'results']) >= 14:
            G.add_edge(w1, w2, weight=1)
    return G

