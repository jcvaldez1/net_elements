#!/bin/bash

rm ./global_req.txt
rm ./poll_req.txt
rm ./poll_res.txt
rm ./countdown.txt

echo "Booting Local Controller"
ryu-manager ~/ndsg_lesgo/testrun.py &
controllerpid=$!
sleep $1

echo "Shutting down controller"
sudo kill -9 $controllerpid
echo "Done"
