#!/Users/teh/code/insight_project/ENV/bin/python
import pickle
import sys
import twitter
import itertools
import networkx as nx

def init_data(query):
    f = open("query_" + query + ".pkl", "r")
    top_results = pickle.load(f)
    f.close()
    return top_results


def init_twitter():
    return twitter.Twitter(domain="search.twitter.com")


def compute_graph(query, top_results, searcher):
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    for w1, w2 in pairs:
        triple = query + " " + w1 + " " + w2
        s = searcher.search(q=triple, lang="en")
        print len(s[u'results'])
        if len(s[u'results']) >= 8:
            G.add_edge(w1, w2, weight=1)
    return G

def pickle_data(data, o_name):
    g = open(o_name, "wb")
    pickle.dump(data, g, -1)

def display_graph(G):
    import matplotlib.pyplot as plt
    nx.draw(G)
    plt.show()


def analyze(query):
    top_results = init_data(query)
    searcher = init_twitter()
    G = compute_graph(query, top_results, searcher)
    pickle_data(G, "graph_" + query + ".pkl")
    display_graph(G)

def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: query'
        sys.exit(1)

    query = args[0]
    analyze(query)

if __name__ == '__main__':
    main()
