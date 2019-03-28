import scapy
import http_scapy
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random
import datetime

class data_analyzer():

    def __init__(self, pcap_name, durations, server_puts):
        self.pcap_name = pcap_name
        self.durations = durations
        self.server_puts = server_puts
        self.tests = 0
        self.block_flag = True
        self.add_flag = False
        self.reply_flag = False

        # set time_stamp vars
        self.udp_timestamp = None
        self.opadd_timestamp = None
        self.oprep_timestamp = None
        self.serverput_timestamp = None

        # average button press to server reception delay
        # server_put - udp_broadcast
        self.user_input_server_travel_time = 0
        
        # average server_reception to ryu openflow flow mod
        # openflow_add - server_put 
        self.user_input_processing_time = 0
        
        # average flow table update time
        # (stat_reply - durations) - openflow_add
        self.flow_table_update = 0
        
        # counters for debugging
        self.udp_count = 0
        self.add_count = 0
        self.rep_count = 0

    def analyze(self, packet):
        
        # get packet type
        packet_type = None
        # catch udp for BLOCKING only
        if (packet_type == "UDP") and (self.block_flag):

            self.udp_timestamp = packet.time
            # get put timestamp that is IMMEDIATELY after udp timestamp
            self.serverput_timestamp = self.server_puts.read()
            self.user_input_server_travel_time += (self.serverput_timestamp - self.udp_timestamp)
            
            # skip the unblocking udp broadcast
            self.block_flag = False
            self.add_flag = True
            self.udp_count += 1

        elif (packet_type == "OPENFLOW ADD 8.8.8.8") and (self.add_flag):
            
            self.opadd_timestamp = packet.time
            # add time between server receive and ryu send to switch         
            self.user_input_processing_time += (self.opadd_timestamp - self.serverput_timestamp)

            self.add_flag = False
            self.reply_flag = True
            self.add_count += 1

        elif (packet_type == "OPENFLOW STAT REPLY") and (self.reply_flag):

            self.oprep_timestamp = packet.time
            # continue on new line
            flow_duration = self.durations.read()

            self.user_input_processing_time += ( (self.oprep_timestamp - flow_duration) - self.opadd_timestamp)
            
            self.reply_flag = False
            self.rep_count += 1
            self.tests += 1
            pass
        else:
            self.block_flag = True

    def sniffer(self): 
        sniff(offline=self.pcap_name,prn=self.analysis,store=0)
        self.tests = float(self.tests)
        if (self.udp_count == self.add_count) and (self.add_count == self.rep_count):
            self.user_input_server_travel_time/= self.tests
            self.user_input_processing_time /= self.tests
            self.flow_table_update /= self.tests
            self.graph_gen()
            # now have average delays
        else:
            print("Packet counters dont lineup")

    def graph_gen(self):
        # make graph that shows average distrib
        pass

if __name__ == "__main__":
    a = data_analyzer(sys.argv[1] , open(sys.argv[2],"r"), open(sys.argv[3]))
    pass

