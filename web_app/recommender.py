import string
import itertools

def find(tweets, cliques):
    recommendations = []
    for clique in cliques:
        rec_tweets = []
        for tweet in tweets:
            norm_tweet = tweet.lower()
            for w in clique:
                if norm_tweet.find(w) > -1:
                    rec_tweets.append(tweet)
                    tweets.remove(tweet)
                    break
        recommendations.append(rec_tweets)
        print(clique)
    return recommendations
