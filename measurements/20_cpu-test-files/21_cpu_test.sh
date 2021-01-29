#!/bin/bash

# run timed linux compulation - no arguments needed
phoronix-test-suite benchmark build-linux-kernel

mkdir ~/benchmark
mkdir ~/benchmark/cpu-test-files
cd ~/benchmark/cpu-test-files || exit

phoronix-test-suite result-file-raw-to-csv cpu-test-v1
phoronix-test-suite result-file-to-csv cpu-test-v1
phoronix-test-suite result-file-to-pdf cpu-test-v1
phoronix-test-suite result-file-to-json cpu-test-v1 >> cpu-test-v1.json

mv ~/cpu-test-v1* .
cp -r ~/.phoronix-test-suite/test-results/cpu-test-v1/ .
