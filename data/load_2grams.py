#!/usr/local/bin/python

import re
import pickle
import string
p = open ('common_words.pkl', 'r')
cw = pickle.load(p)
cw.append("")

number = "45"
input_file = 'googlebooks-eng-1M-2gram-20090715-' + number + '.csv'
output_file = '1M-2gram-' + number + '-head.csv'
f = open(input_file,'r')
g = open(output_file,'w')
write_lines = 0
lines_read = 0
number_and_ampersand = "[0-9&']"
non_word_and_space = "[^\w\s]"
for line in f.xreadlines():
    lines_read += 1
    if lines_read % 100000 == 0:
        print "Line: " + str(lines_read)

    if re.search("200", line) is not None:
        a = line.split()
        if (re.search(number_and_ampersand,a[0]) is None and
            re.search(number_and_ampersand,a[1]) is None and
            int(a[3]) >= 10):
            a[0] = re.sub(non_word_and_space,"",a[0]).lower()
            a[1] = re.sub(non_word_and_space,"",a[1]).lower()
            if a[0] not in cw and a[1] not in cw:
                g.write(string.join(a) + '\n')
                write_lines += 1

    #if write_lines >= 1000:
    #    break

f.close()
g.close()

def main():
  args = sys.argv[1:]

  if not args:
    print 'usage: ./load_2grams.py number'
    sys.exit(1)

  todir = ''
  if args[0] == '--todir':
    todir = args[1]
    del args[0:2]

  img_urls = read_urls(args[0])

  if todir:
    download_images(img_urls, todir)
  else:
    print '\n'.join(img_urls)

if __name__ == '__main__':
  main()
