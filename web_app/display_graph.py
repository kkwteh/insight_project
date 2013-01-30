#!/Users/teh/code/insight_project/ENV/bin/python
import pickle
import sys
import networkx as nx
import matplotlib.pyplot as plt

def init_data(query):
    f = open("graph_" + query + ".pkl", "r")
    G = pickle.load(f)
    f.close()
    return G


def show_graph(G):
    nx.draw(G)
    plt.show()

def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: query'
        sys.exit(1)

    query = args[0]
    G = init_data(query)
    show_graph(G)

if __name__ == '__main__':
    main()
