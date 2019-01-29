import netifaces as ni
import constants
import subprocess
import ast

def get_host_ip():
    ip_not_found = True
    counter = 1
    ip = "N/A"
    while ip_not_found:
        try:
            interface = "h" + str(counter) + "-eth0"
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            ip_not_found = False
        except:
            counter = counter + 1
    return(ip)

def get_packet_list(): 
    python_command = ['python' ,constants.REQUEST_NATURE_SCRIPT ,constants.PCAP_FILE_NAME]
    proc = subprocess.Popen(python_command,stdout=subprocess.PIPE)
    list_packets = proc.stdout.read()
    list_packets = list_packets.decode()
    list_packets_new = list_packets[:len(list_packets)-1]
    list_packets = ast.literal_eval(list_packets_new)
    return list_packets

