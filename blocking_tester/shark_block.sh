#!/bin/bash

touch block_trace.pcap
tshark -i enp3s0f0 -a duration:600 -w ./block_trace.pcap & ping 8.8.8.8 & python3 block_test.py
