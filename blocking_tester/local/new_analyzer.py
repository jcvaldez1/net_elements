#import scapy
#from scapy.all import *
#from scapy_http import http
#from tldextract import *
import math
import random
import datetime
import argparse, sys
import matplotlib.pyplot as plt

class data_analyzer():

    def __init__(self, arguments):
        args = arguments
        #self.pcap_name = args.pcap
        self.udp_flags = open(args.flags, "r")
        self.flow_mods = args.flowmods
        self.durations = args.durations
        self.server_puts = args.serverlogs
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

        self.sum = 0
    def analyze(self):
        



        # RETRIEVE CORRESPONDING PUT TIMESTAMP
        #self.serverput_timestamp = self.server_puts.read()
        #print(str(self.udp_timestamp))
        f = open(self.server_puts,"r")
        for line in f:
            temp_time = datetime.datetime.strptime(line[5:28], "%Y-%m-%d %H:%M:%S,%f")
            #print(str(temp_time) + " " + line[-3:-1])
            if (temp_time > self.udp_timestamp) and (line[-3:-1] == '30'):
                self.serverput_timestamp = temp_time
                break
        f.close() 

        # RETRIEVE CORRESPONDING OPADD TIMESTAMP
        #self.serverput_timestamp = self.server_puts.read()
        f = open(self.flow_mods,"r")
        for line in f:
            temp_time = datetime.datetime.strptime(line,"%Y-%m-%d %H:%M:%S.%f\n")
            if (temp_time > self.serverput_timestamp):
                self.opadd_timestamp = temp_time
                break
        f.close() 

        # RETRIVE THE CORRESPONDING FLOW ADDITION TIMESTAMP
        f = open(self.durations, "r")
        for line in f:
            temp_time = datetime.datetime.strptime(line[:26], "%Y-%m-%d %H:%M:%S.%f")
            if (temp_time > self.opadd_timestamp):
                self.oprep_timestamp = (temp_time)
                duration = float(line[-5:]) * (10**6) 
                #print(str(self.oprep_timestamp.microsecond-duration))
                self.oprep_timestamp = self.oprep_timestamp.replace(microsecond=int(self.oprep_timestamp.microsecond-duration))
                break
        f.close() 
        
        self.user_input_server_travel_time += (self.serverput_timestamp - self.udp_timestamp).total_seconds()
        self.user_input_processing_time += (self.opadd_timestamp - self.serverput_timestamp).total_seconds()
        self.flow_table_update += (self.oprep_timestamp - self.opadd_timestamp).total_seconds()
        self.tests += 1


    # OLD SHIT BAD PRACTICE OMEGA LUL
    def old_analyze(self):
        if (packet_type == "UDP") and (self.block_flag):

            self.udp_timestamp = packet.time
            # get put timestamp that is IMMEDIATELY after udp timestamp
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
        #sniff(offline=self.pcap_name,prn=self.analyze,store=0)
        # iterate through udp flag timestamps
        for line in self.udp_flags:
            self.udp_timestamp = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
            self.analyze()
            pass

        self.tests = float(self.tests)
        self.user_input_server_travel_time/= self.tests
        self.user_input_processing_time /= self.tests
        self.flow_table_update /= self.tests
        self.sum = self.user_input_server_travel_time + self.user_input_processing_time + self.flow_table_update
        print(str(self.user_input_server_travel_time))
        print(str(self.user_input_processing_time))
        print(str(self.flow_table_update))
        self.graph_gen()
        # now have average delays

    def graph_gen(self):
        # make graph that shows average distrib
        labels = 'User input to Controller', 'Controller processing', 'Flow Update Delay'
        
        sizes = [self.user_input_server_travel_time/self.sum, self.user_input_processing_time/self.sum, self.flow_table_update/self.sum]
        colors = ['gold', 'yellowgreen', 'lightcoral']
        #explode = (0.1, 0, 0, 0)  # explode 1st slice

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
         
        plt.axis('equal')
        plt.show()

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    #parser.add_argument('--pcap', help='pcap file')
    parser.add_argument('--flags', help='udp flags file')
    parser.add_argument('--flowmods', help='flow mod timestamps file')
    parser.add_argument('--serverlogs', help='serverlogs file')
    parser.add_argument('--durations', help='flow durations file')
    args=parser.parse_args()
    a = data_analyzer(args)
    a.sniffer()
    pass

