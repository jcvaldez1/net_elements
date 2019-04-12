#!/bin/bash

rm ./block_trace.pcap
rm ./poll_req.txt
rm ./poll_res.txt
rm ./countdown.txt
rm ./global_test.txt
rm ./global_rest.txt
touch block_trace.pcap

echo "Booting Up Server"
python3 ~/local_controller/manage.py runserver &
serverpid=$!

sleep 30s
echo "Server booted"

echo "Booting Local Controller"
ryu-manager ~/ndsg_lesgo/theft_tester.py &
controllerpid=$!
sleep $1

echo "Shutting down controller"
sudo kill -9 $controllerpid
echo "Shutting down server"
sudo kill -9 $serverpid

echo "Done"
echo "check block_trace.pcap for details"
