#!/bin/bash

for i in `seq 101 112`
do
ip="172.20.$i.101"
python auto_netcat.py -t $ip
done
