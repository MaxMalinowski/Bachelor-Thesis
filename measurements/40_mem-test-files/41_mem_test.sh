#!/bin/bash

# run stream - 5
phoronix-test-suite benchmark stream 
# run ramspeed - 6, 3
phoronix-test-suite benchmark ramspeed   

mkdir ~/benchmark
mkdir ~/benchmark/mem-test-files
cd ~/benchmark/mem-test-files || exit

phoronix-test-suite result-file-raw-to-csv mem-test-v1
phoronix-test-suite result-file-to-csv mem-test-v1
phoronix-test-suite result-file-to-pdf mem-test-v1
phoronix-test-suite result-file-to-json mem-test-v1 >> mem-test-v1.json

mv ~/mem-test-v1* .
cp -r ~/.phoronix-test-suite/test-results/mem-test-v1/ .

phoronix-test-suite result-file-raw-to-csv mem-test-v2
phoronix-test-suite result-file-to-csv mem-test-v2
phoronix-test-suite result-file-to-pdf mem-test-v2
phoronix-test-suite result-file-to-json mem-test-v2 >> mem-test-v2.json

mv ~/mem-test-v2* .
cp -r ~/.phoronix-test-suite/test-results/mem-test-v2/ .