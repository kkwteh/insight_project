#!/usr/local/bin/python

import sys
import re
import string
import MySQLdb

def load(number):
    input_file = '1M-2gram-' + number + '-head.csv'
    f = open(input_file,'r')
    con = MySQLdb.connect('localhost','root','','ngram_test_db')
    with con:
        cur = con.cursor()
        for line in f.xreadlines():
            a = line.split()
            command = "INSERT INTO twograms VALUES(NULL, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(a[0],a[1],a[2],a[3],a[4],a[5])
            cur.execute(command)
    f.close()

def main():
    args = sys.argv[1:]
    if not args:
        print 'usage: ./load_database.py number'
        sys.exit(1)
    number = args[0]
    load(number)


if __name__ == '__main__':
    main()
