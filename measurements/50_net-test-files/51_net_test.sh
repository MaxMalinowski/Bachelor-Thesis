#!/bin/bash

# run netperf - [1, 2, 4, 5, 6], 1
phoronix-test-suite benchmark netperf

# run ping
ping 10.1.1.1 -c 100 >> net-test-v1-ping-gateway.txt
ping 8.8.8.8 -c 100 >> net-test-v1-ping-partner.txt

mkdir ~/benchmark
mkdir ~/benchmark/net-test-files
cd ~/benchmark/net-test-files || exit

phoronix-test-suite result-file-raw-to-csv net-test-v1
phoronix-test-suite result-file-to-csv net-test-v1
phoronix-test-suite result-file-to-pdf net-test-v1
phoronix-test-suite result-file-to-json net-test-v1 >> net-test-v1.json

mv ~/net-test-v1* .
cp -r ~/.phoronix-test-suite/test-results/net-test-v1/ .
