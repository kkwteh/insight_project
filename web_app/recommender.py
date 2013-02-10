import string
import itertools

def find(tweets, cliques):
    cluster_ids_all = []
    clique_strings = []
    for clique in cliques:
        rec_tweets = []
        for tweet in tweets:
            norm_tweet = tweet['text'].lower()
            for w in clique:
                if norm_tweet.find(w) > -1:
                    rec_tweets.append(tweet['id'])
                    break
        clique_string = " ".join(clique)
        cluster_ids_all.append(rec_tweets)
        clique_strings.append(clique_string)
        print(clique)
    return cluster_ids_all, clique_strings
