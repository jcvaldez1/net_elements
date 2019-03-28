# RUN THIS SCRIPT FOR CLIENT SIDE HOST
import socket
import net_elements
import constants
import subprocess
import ast
import utilities as util
import sys

def ip_map(dest_list):
    # call this for mininet setups only
    pass


def client_start(mode="GENUINE"):
    raw_data = util.get_packet_list(mode)
    packet_list = {}

    counter = 0
    for x in raw_data:
        counter = counter + 1
        # check if client IP is already recognized
        index = x[4][0]
        destination = x[4][1]
        destination = "10.0.0.2" # THIS IS TEMPORARY
        new_packet = net_elements.Packet( src_ip=index, dst_ip=destination, delay=x[2],
                                          payload_size=x[1], response_size=x[3],
                                          connection_ender= True if x[5] == 1 else False)

        if counter == len(raw_data):
            new_packet.ender = True
        #if (counter == len(raw_data)) or (counter == len(raw_data)/2):
        #    # force connection ender packet for the last one
        #    new_packet.ender = True
        packet_list.setdefault(index, []).append(new_packet)

    print(len(packet_list))
    for source_ip, packet_list in packet_list.items():
        temp = net_elements.Client( address=source_ip, packet_list=packet_list)
        temp.activate()
    



if __name__ == "__main__":
    client_start(sys.argv[1])
