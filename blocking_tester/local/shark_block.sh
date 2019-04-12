#!/bin/bash

rm ./block_trace.pcap
rm ./logs.log
rm ./shit.txt
rm ./flags_block.txt
rm ./flowmods.txt
touch block_trace.pcap

echo "Booting Up Server"
#python3 ~/local_controller/manage.py runserver;
#rm ~/local_controller/localController/logs.log
sudo python3 ~/local_controller/manage.py runserver &
serverpid=$!
sleep 30s
echo "Server booted"
echo "Booting Local Controller"
ryu-manager ~/ndsg_lesgo/INTERVAL_TEST.py &
controllerpid=$!
echo "Initializing sharker..."
#tshark -i enp3s0f0 -a duration:$(($1 + 10)) -w ./block_trace.pcap & 
sleep 30s
#sharkpid=$!

#ping 8.8.8.8 &
#ping -i 0.5 -W 0.5 8.8.8.8 &
#pingpid=$!
modified=$(( $1/10 ))
python3 block_test.py --duration $(( $modified-1 ))
#pypid=$!


#sleep $(($1 + 10))

#sudo kill -9 $pingpid
#sudo kill -9 $pypid
echo "Shutting down controller"
sudo kill -9 $controllerpid
echo "Shutting down server"
sudo kill -9 $serverpid

echo "Done"
echo "check block_trace.pcap for details"
#echo "Running analyzer Script"
#touch blocking_results.txt;
#chmod 755 blocking_results.txt;
#python analyzer.py ./block_trace.pcap > blocking_results.txt;
#echo "run graph test for results"
