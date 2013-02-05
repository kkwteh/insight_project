#!/Users/teh/code/insight_project/ENV/bin/python

import pickle
import pdb
import operator
from nltk.corpus import wordnet as wn

dolphins = ['google', 'apple',  'beckham',  'superbowl',  'justin',  'jaibrooks',  'jaifollowmeyoupeasant', 'justinbieber',   '49ers',   'reina',  'liam',  'bieber',  'ipad',  'beliebers',  'chris',  'gerrard',  'joe',  'starbucks',  'lakers',  'edsheeran',  'itunes',  'rihanna',  'hagel',  'chelsea',  'selena',  'steve',  'jim',  'sturridge',  'nba',  'netflix',  'jackie',  'mcdonalds', 'kevin',  'steven',  'balotelli',  'xbox',  'francisco',  'skype',  'richard',  'espn', 'ravens', 'iphone', 'instagram', 'french', 'uk', 'american', 'london', 'english', 'internet', 'basketball', 'players', 'health', 'public', 'america', 'heaven']
f = open("twitter_word_count.pkl", "r")
count = pickle.load(f)
sorted_count = sorted(count.iteritems(), key=operator.itemgetter(1))
sorted_count.reverse()
sorted_count = [(a,b) for (a,b) in sorted_count if (b > 100 and
                                                a not in dolphins)]
f.close()
output = open("top_twitter_words.pkl", "wb")
pickle.dump(sorted_count, output, -1)
output.close()
