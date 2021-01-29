#!/bin/bash

# run fio - 5, 4, 2, 2, 1
phoronix-test-suite benchmark fio

# run ioping
sudo ioping -D -c 100 / >> ~/disk-test-v1-ping.txt

mkdir ~/benchmark
mkdir ~/benchmark/disk-test-files
cd ~/benchmark/disk-test-files || exit

phoronix-test-suite result-file-raw-to-csv disk-test-v1
phoronix-test-suite result-file-to-csv disk-test-v1
phoronix-test-suite result-file-to-pdf disk-test-v1
phoronix-test-suite result-file-to-json disk-test-v1 >> disk-test-v1.json

mv ~/disk-test-v1* .
cp -r ~/.phoronix-test-suite/test-results/disk-test-v1/ .
