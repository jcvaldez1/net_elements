import net_elements
import socket
import constants
import subprocess
import ast
import netifaces as ni
import utilities as util

def server_start():    
    my_ip = util.get_host_ip()
    print(str(my_ip))
    # my_ip = "10.0.0.2"

    # raw_data = util.get_packet_list()
    # RAW_DATA OUTPUT
    #         pay     delay time       resp      src_ip            dst_ip   conn_ender
    # ('TCP', 58, 0.003567868470993611, 42, ('10.147.80.139', '10.16.5.225'), 0)

    #is_server = False
    #for x in raw_data:
    #    # CHECK IF THIS HOST IS PART OF THE DESTINATIONS
    #    index = x[4][1]
    #    if index == my_ip:
    #        is_server = True

    is_server = True
    if is_server:
        # starts the server up
        this_server = net_elements.Server(address=my_ip)
        this_server.start_socket()
    #
    #else:
    #    print("SERVER DOESNT HAVE IP AS A DESTINATION!")
    #    # TEMPORARY FIX DONT REMOVE UNTIL
    #    # MININET HOST IP CAN BE CONFIGURED
    #    #this_server = net_elements.Server(address=my_ip)
    #    #this_server.start_socket()


if __name__ == "__main__":
    server_start()



