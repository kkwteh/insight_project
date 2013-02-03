#!/bin/bash

mongod &
MONGOID=$!


while [ 0 -lt 1 ]
do
./twitter_stream.py
PYID=$!
sleep 5
kill $PYID
done
