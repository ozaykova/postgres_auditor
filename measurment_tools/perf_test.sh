#!/bin/sh

for clients in 1 10 20 30 40 50 60 70 80 90 100 110 120 150 200 300 400 500 600 700 800 900 1000
do
        echo "RC ${clients}"
        pgbench -j 4 -c $clients -v demo
done