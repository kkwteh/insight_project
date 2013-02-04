import pages_getter
import networkx as nx
import twitter
import itertools

def compute_graph(query, top_results, tweets):
    searcher = pages_getter.init_twitter()
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    i = 0
    query_list, page_nums = [],[]
    for w1, w2 in pairs:
        query_list.append(query + " " + w1 + " " + w2)
        page_nums.append(1)

    per_page = 15
    pages_with_queries  = pages_getter.get_pages_of_tweets(searcher, query_list, page_nums, per_page)
    for query, page in pages_with_queries:
        w1 = query.split()[1]
        w2 = query.split()[2]
        print len(page)
        if len(page) >= 14:
            G.add_edge(w1, w2, weight=1)
    return G

