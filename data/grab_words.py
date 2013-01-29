import pickle
f = open("top_5000_words.txt", 'r')
g = open("top_5000.pkl", 'wb')

top_5000 = []

for line in f.xreadlines():
    a = line.split()
    top_5000.append(a[1])

pickle.dump(top_5000, g, -1)
f.close()
g.close()
