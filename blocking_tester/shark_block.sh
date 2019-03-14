#!/bin/bash

touch block_trace.pcap


tshark -i enp3s0f0 -a duration:300 -w ./block_trace.pcap & 
sharkpid=$!

ping 8.8.8.8 &
pingpid=$!
 
python3 block_test.py &
pypid=$!


sleep 330

#kill -SIGKILL $sharkpid
kill -SIGKILL $pingpid
kill -SIGKILL $pypid
