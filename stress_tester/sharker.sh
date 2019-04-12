# !/bin/bash
rm ./stress.pcap
touch ./stress.pcap

sudo tshark -i enp3s0f0 -w stress.pcap
