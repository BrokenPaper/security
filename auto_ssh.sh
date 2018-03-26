#!/bin/bash
# 配合 auto_ssh.py
for i in `seq 2 5`
do
ip="192.168.100.$i"
echo "[SSH] Attack $ip..."
a=`nc -z $ip 22 -v -n -w 1 2>&1|grep open|wc -l`
if [ "$a" -eq "1" ]
then
python auto_ssh.py -t $ip
fi
done
