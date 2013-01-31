import tweet_slicer
import string

def find(query, cliques):
    searcher = tweet_slicer.init_twitter()
    recommendations = []
    for c in cliques:
        c.append(query)
        clique_query = "%20".join(c)
        search_data = searcher.search(q=clique_query, lang="en", rpp=1)
        print clique_query
        if search_data[u'results'] != []:
            tweet = search_data[u'results'][0][u'text']
            recommendations.append((clique_query, tweet))
    return recommendations
