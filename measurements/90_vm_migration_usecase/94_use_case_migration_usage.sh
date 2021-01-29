#!/bin/bash

cnt=0
no=1000
results='/opt/stack/benchmark/migration-vm.txt'

cat /proc/meminfo | grep 'MemTotal'> $results
echo "
------
" >> $results

echo "Measuring idle stats ..."
while [ $cnt -lt $no ];
do
        date +%s >> $results
        cat /proc/meminfo | grep 'MemFree'>> $results
        sar 1 5 | grep 'Average' | sed 's/^.* //' >> $results
        echo " " >> $results
        cnt=$((cnt + 1))
done

echo "Test done!"
