import pages_getter
import networkx as nx
import twitter
import itertools
import random

def compute_graph(query, top_results, tweets):
    searcher = pages_getter.init_twitter()
    G = nx.Graph()
    G.add_nodes_from(top_results)
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    i = 0
    query_list, page_nums = [],[]
    for w1, w2 in pairs:
        query_list.append(w1 + " " + w2 + " " + query)
        page_nums.append(1)
    random.shuffle(query_list)

    per_page = 15
    pages_with_queries  = pages_getter.get_pages_of_tweets(searcher, query_list, page_nums, per_page)
    for query, page in pages_with_queries:
        w1 = query.split()[0]
        w2 = query.split()[1]

        for tweet in page[:]:
            text = tweet[u'text'].lower()
            if text.find(w1) == -1 or text.find(w2) == -1:
                page.remove(tweet)
        print len(page), w1, w2
        if len(page) >= 10:
            for tweet in page:
                text = tweet[u'text']
            G.add_edge(w1, w2, weight=1)
    return G

