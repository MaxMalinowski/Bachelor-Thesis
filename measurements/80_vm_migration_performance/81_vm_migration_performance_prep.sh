#!/bin/bash

printf 'NEW MEASUREMENTS - ' > /home/ubuntu/migration-performance.txt
python3 -c "import time
print(time.time())" >> /home/ubuntu/migration-performance.txt
printf '\n' >> /home/ubuntu/migration-performance.txt
