import datetime
import argparse, sys
import matplotlib.pyplot as plt

from scapy.all import *
from scapy_http import http
from tldextract import *



class DataAnalyzer():
    def __init__(self, arguments):
        args = arguments
        #self.pcap_name = args.pcap
        self.get_flags = args.flags
        self.flow_mods = open(args.flowmods, "r")
        self.durations = args.durations
        self.server_puts = args.serverlogs
        self.tests = 0
        self.block_flag = True
        self.add_flag = False
        self.reply_flag = False

        # set time_stamp vars
        self.get_req_timestamp = None
        self.opadd_timestamp = None
        self.oprep_timestamp = None
        self.get_ok_timestamp = None

        # global controller response time
        # http ok - http get
        self.global_req_time = 0
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

        self.GET_CAUGHT = False
        self.CATCH_OK = False
        self.latest_finack = None
        #open(self.get_flags, 'w').close()
    def analyze(self):
        global_req_adder = 0
        # RETRIEVE CORRESPONDING OPADD TIMESTAMP
        #self.get_ok_timestamp = self.server_puts.read()
        f = open(self.get_flags,"r")
        temp_time = None
        prev_time = None
        for line in f:
            temp_time = datetime.strptime(line[:26], "%Y-%m-%d %H:%M:%S.%f")
            if (temp_time > self.opadd_timestamp):
                if not prev_time:
                    prev_time = temp_time
                self.get_ok_timestamp = prev_time
                break
            prev_time = temp_time
            global_req_adder = float(line[27:])
        f.close()

        # RETRIVE THE CORRESPONDING FLOW ADDITION TIMESTAMP
        f = open(self.durations, "r")
        for line in f:
            temp_time = datetime.strptime(line[:26], "%Y-%m-%d %H:%M:%S.%f")
            if (temp_time > self.opadd_timestamp):
                self.oprep_timestamp = (temp_time)
                duration = float(line[-5:]) * (10**6)
                #print(str(self.oprep_timestamp.microsecond-duration))
                self.oprep_timestamp = self.oprep_timestamp.replace(microsecond=int(self.oprep_timestamp.microsecond-duration))
                break
        f.close()
        self.global_req_time += global_req_adder
        self.user_input_processing_time += (self.opadd_timestamp - self.get_ok_timestamp).total_seconds()
        self.flow_table_update += (self.oprep_timestamp - self.opadd_timestamp).total_seconds()
        self.tests += 1

    def sniffer(self, packet):
        FIN = 0x01
        SYN = 0x02
        ACK = 0x10
        # iterate through udp flag timestamps
        # RETRIEVE DNS TIMESTAMP
        if (packet.haslayer(UDP)) and ("GET should be" in str(packet.payload)):
            self.get_req_timestamp = datetime.utcfromtimestamp(packet.time/1000.0)
            self.GET_CAUGHT = True
        # CATCH OK
        elif (self.CATCH_OK) and (packet.haslayer(UDP)) and ("OK should be" in str(packet.payload)):
            # CATCH REPLY
            #self.get_ok_timestamp = datetime.utcfromtimestamp(self.latest_finack.time/1000.0)
            self.get_ok_timestamp = datetime.utcfromtimestamp(packet.time/1000.0)
            # ADD TO VAR
            self.reply_flag = True
            self.CATCH_OK = False
        elif packet.haslayer(TCP):
            if (packet["TCP"].flags & FIN) and (packet["TCP"].flags & ACK) and (packet["IP"].src == "10.147.4.52"):
               self.latest_finack = packet
        # CATCH CORRESPONDING DNS
        elif (packet.haslayer(DNS)) and (self.GET_CAUGHT):
            #self.get_req_timestamp = datetime.utcfromtimestamp(packet.time/1000.0)
            self.GET_CAUGHT = False
            self.CATCH_OK = True

        # record timestamps to file
        if (self.reply_flag):
            self.file_record()
            self.reply_flag = False

    def file_record(self):
        delay = (self.get_ok_timestamp - self.get_req_timestamp ).total_seconds()

        f = open(self.get_flags,'a+')
        stringy = str(self.get_ok_timestamp) + " " + str(delay) + "\n"
        f.write(stringy)
        f.close()

    def startify(self):

        #sniff(offline="block_trace.pcap",prn=self.sniffer,store=0)

        # NOW ANALYZE
        for line in self.flow_mods:
            self.opadd_timestamp = datetime.strptime(line,"%Y-%m-%d %H:%M:%S.%f\n")
            self.analyze()
        
        self.tests = float(self.tests)
        self.global_req_time /= self.tests
        self.user_input_processing_time /= self.tests
        self.flow_table_update /= self.tests
        self.sum = self.global_req_time + self.user_input_processing_time + self.flow_table_update
        print(str(self.global_req_time))
        print(str(self.user_input_processing_time))
        print(str(self.flow_table_update))
        self.graph_gen()
        # now have average delays

    def graph_gen(self):
        # make graph that shows average distrib
        labels = 'Global controller GET', 'Controller processing', 'Flow Update Delay'
        sizes = [self.global_req_time/self.sum, self.user_input_processing_time/self.sum, self.flow_table_update/self.sum]
        colors = ['gold', 'yellowgreen', 'lightcoral']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
        plt.axis('equal')
        plt.show()

if __name__ == "__main__":
    pars = argparse.ArgumentParser()
    pars.add_argument('--flags', help='udp flags file')
    pars.add_argument('--flowmods', help='flow mod timestamps file')
    pars.add_argument('--serverlogs', help='serverlogs file')
    pars.add_argument('--durations', help='flow durations file')
    argums=pars.parse_args()
    a = DataAnalyzer(argums)
    a.startify()

