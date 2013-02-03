#!/Users/teh/code/insight_project/ENV/bin/python

import pickle
import pdb
import operator

f = open("twitter_word_count.pkl", "r")
count = pickle.load(f)
sorted_count = sorted(count.iteritems(), key=operator.itemgetter(1))
sorted_count.reverse()
pdb.set_trace()
