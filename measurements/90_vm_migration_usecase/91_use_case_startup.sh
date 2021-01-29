#!/bin/bash

cnt=0
no1=40
no2=60
no3=80
no4 120
results='/opt/stack/benchmark/startup-test.txt'

cat /proc/meminfo | grep 'MemTotal'> $results
echo "
------
" >> $results

echo "Measuring idle stats ..."
while [ $cnt -lt $no1 ];
do
        date +%s >> $results
        cat /proc/meminfo | grep 'MemFree'>> $results
        sar 1 5 | grep 'Average' | sed 's/^.* //' >> $results
        echo " " >> $results
        cnt=$((cnt + 1))
done

echo "Starting vm ..."
. /opt/stack/devstack/openrc admin demo 
nova start test-vm

echo "Measuring load stats ..."
while [ $cnt -lt $no2 ];
do
        echo "$cnt"
        date +%s >> $results
        cat /proc/meminfo | grep 'MemFree'>> $results
        sar 1 5 | grep 'Average' | sed 's/^.* //' >> $results
        echo " " >> $results
        cnt=$((cnt + 1))
done

echo "Starting VNC server ..."
while [ $cnt -lt $no3 ];
do
        echo "$cnt"
        date +%s >> $results
        cat /proc/meminfo | grep 'MemFree'>> $results
        sar 1 5 | grep 'Average' | sed 's/^.* //' >> $results
        echo " " >> $results
        cnt=$((cnt + 1))
done

echo "Starting Tetris ..."
while [ $cnt -lt $no4 ];
do
        echo "$cnt"
        date +%s >> $results
        cat /proc/meminfo | grep 'MemFree'>> $results
        sar 1 5 | grep 'Average' | sed 's/^.* //' >> $results
        echo " " >> $results
        cnt=$((cnt + 1))
done

echo "Test done!"