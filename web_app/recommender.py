import string
import itertools

def find(tweets, cliques):
    recommendations = []
    for clique in cliques:
        rec_tweets = []
        for tweet in tweets:
            norm_tweet = tweet['text'].lower()
            for w in clique:
                if norm_tweet.find(w) > -1:
                    rec_tweets.append(tweet['id'])
                    break
        rec_column_length = 10
        clique_string = " ".join(clique)
        recommendations.append([rec_tweets[:rec_column_length], clique_string])
        print(clique)
    return recommendations
