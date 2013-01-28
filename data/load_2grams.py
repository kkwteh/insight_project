#!/usr/local/bin/python

import re
number = "45"
input_file = 'googlebooks-eng-1M-2gram-20090715-' + number + '.csv'
output_file = '1M-2gram-' + number + '-head.csv'
f = open(input_file,'r')
g = open(output_file,'w')
write_lines = 0
number_and_ampersand = '[0-9&]'
non_word_and_space = "[^\w\s]"
for line in f.xreadlines():
    if re.search("200", line) is not None:
        a = line.split()



        if (re.search(number_and_ampersand,a[0]) is None and
            re.search(number_and_ampersand,a[1]) is None):
            a[0] = re.sub(non_word_and_space,"",a[0]).lower()
            a[1] = re.sub(non_word_and_space,"",a[1]).lower()
            if a[0] is not "" and a[1] is not "":
                g.write(line)
                write_lines += 1

    if write_lines >= 1000:
        break

    # <tokenize line>
    #     <strip zeroth and first elements of punctuation and downcase them>
    #     <if second element has "200"> and <if zeroth element and first element are nonempty, load pair into mysql db uniquely>
    # if (re.search("200", line) != None and
    #     re.search('[^\w\s"]', line) == None and
    #     re.search('""', line) == None):
    #     g.write(line)

f.close()
g.close()
