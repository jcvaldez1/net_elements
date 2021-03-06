import sys
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random


class analyzer:
    
    def __init__(self, pcap_name):
        self.pcap_name = pcap_name
        self.throughput = {}
        self.responses = {}
        self.signals = []
        self.key_order = []
        self.first = 0
        self.PACKET_SIZE=48
        self.first_flag = True        

    def analysis(self, packet):

        if self.first_flag:
            self.first = packet.time
            self.first_flag = False

        if "ICMP" in packet:
            pkt = packet["ICMP"]
            if pkt.type == 8:
                self.responses[pkt.seq] = packet.time - self.first
                self.key_order.append(packet.time - self.first)

            elif (pkt.type == 0) and (pkt.seq in self.responses):
                self.throughput[packet.time - self.first] = len(packet["ICMP"].payload)
                self.key_order.append(packet.time - self.first)
                self.key_order.remove(self.responses[pkt.seq])
                del self.responses[pkt.seq]
            #print(str(packet["ICMP"].seq) + " " + str(packet["ICMP"].type))    

        if "UDP" in packet:
            if "test" in str(packet["UDP"].payload):
                self.signals.append(packet.time - self.first)
    def analyze(self):
        sniff(offline=self.pcap_name,prn=self.analysis,store=0)

    def generate_graph(self):
        # generate dash line marks for signals
        local_seq_list = []
        for word in self.seq_list:
            if word not in local_seq_list:
                local_seq_list.append(word)

        string = "x y\n"
        for x in self.signals:
            temp = str(x) + " 0\n"
            temp = temp + str(x) + " " + "2\n"
            string = string + temp
        print(string)

        # generate responded and unresponded packet flags
        string = "x y\n"
        for x in local_seq_list:
            add_string = 5
            if x in self.responses:
                add_string = str(self.responses[x]) + " 1"
                pass
            elif x in self.unresponded_requests:
                add_string = str(self.unresponded_requests[x]) + " 0"
                pass

            temp = add_string + "\n"
            string = string + temp

        print(string)

if __name__ == '__main__':
    a = analyzer(sys.argv[1])
    a.analyze()
    a.generate_graph()
    #print(str(a.__dict__))
