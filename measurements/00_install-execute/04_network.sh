#!/bin/bash
phoronix-test-suite benchmark netperf
ping gateway -c 100
ping partner -c 100
