#!/bin/bash

# establish cronjob at reboot 
# @reboot /home/ubuntu/81_vm_migration_performance_prep.sh
# * * * * * /home/ubuntu/82_vm_migration_performance_run.sh

results="/home/ubuntu/migration-performance.txt"

python3 -c "import time
print(time.time())" >> "$results"
sysbench --max-time=1 --threads=1 cpu run | grep -e "events per second" -e "avg:" >> "$results"
echo "
---
" >> "$results"