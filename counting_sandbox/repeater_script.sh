#!/bin/bash

mongod &
MONGOID=$!
sleep 5
while [ 0 -lt 1 ]
do
./twitter_stream.py
PYID=$!
sleep 60
kill $PYID
done
