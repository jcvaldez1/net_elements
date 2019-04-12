#!/bin/bash

rm ./block_trace.pcap
rm ./logs.log
rm ./shit.txt
rm ./flags_block.txt
rm ./flowmods.txt
rm ./getters.txt
rm ./newboy.txt
touch block_trace.pcap

echo "Booting Up Server"
python3 ~/local_controller/manage.py runserver &
serverpid=$!

sleep 30s
echo "Server booted"

echo "Booting Local Controller"
ryu-manager ~/ndsg_lesgo/INTERVAL_TEST.py &
controllerpid=$!
tshark -i enp3s0f0 -a duration:$(($1 + 300)) -w ./block_trace.pcap & 
sharkpid=$!
sleep 30s

modified=$(( $1/20 ))
python3 block_test.py --duration $(( $modified-1 ))

echo "Shutting down controller"
sudo kill -9 $controllerpid
echo "Shutting down server"
sudo kill -9 $serverpid
echo "Shutting down sharker"
sudo kill -9 $sharkpid

echo "Done"
echo "check block_trace.pcap for details"
