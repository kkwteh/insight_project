#!/usr/local/bin/python
import pickle
import sys
import twitter
import itertools

def init_data(query):
    f = open("query_" + query + ".pkl", "r")
    top_results = pickle.load(f)
    f.close()
    pairs = [(x,y) for (x,y) in itertools.product(top_results,repeat = 2) if x < y ]
    return pairs


def init_twitter():
    return twitter.Twitter(domain="search.twitter.com")


def compute_distances(query, pairs, searcher):
    distance_matrix = {}
    for w1, w2 in pairs:
        triple = query + " " + w1 + " " + w2
        s = searcher.search(q=triple, lang="en")
        print len(s[u'results'])
        d = 1.0/(0.1 + len(s[u'results']))
        distance_matrix[(w1,w2)] = d
    return distance_matrix

def pickle_data(data, o_name):
    g = open(o_name, "wb")
    pickle.dump(data, g, -1)

def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: query'
        sys.exit(1)

    query = args[0]
    pairs = init_data(query)
    searcher = init_twitter()
    distance_matrix = compute_distances(query, pairs, searcher)
    pickle_data(distance_matrix, "distances_" + query + ".pkl")


if __name__ == '__main__':
    main()
