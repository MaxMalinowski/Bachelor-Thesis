#!/bin/bash
cnt=0
results="$HOME/benchmark/startup-test.txt"
cat /proc/meminfo | grep 'MemTotal'> "$results"

while [ $cnt -lt 100 ]; do
    if [ $cnt -eq 40 ]; then
        . $HOME/devstack/openrc admin demo && nova start test-compute-vm
    fi
    date +%s >> "$results"
    cat /proc/meminfo | grep 'MemFree'>> "$results"
    sar 1 5 | grep 'Average' | sed 's/^.* //' >> "$results"
    echo " " >> $results
    cnt=$((cnt + 1))
done
