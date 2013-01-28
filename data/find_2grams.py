import re
number = "45"
input_file = 'googlebooks-eng-1M-2gram-20090715-' + number + '.csv'
f = open(input_file,'r')
for index, line in enumerate(f.xreadlines()):
    if re.search('-', line) == None:
            print(line)

f.close()
