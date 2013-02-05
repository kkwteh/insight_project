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
        if len(rec_tweets) > 3:
            clique_string = " ".join(clique)
            recommendations.append([rec_tweets[:3], clique_string])
        print(clique)
    return recommendations
