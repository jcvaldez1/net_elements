import sys
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random


class analyzer:
    
    def __init__(self, pcap_name):
        self.pcap_name = pcap_name
        self.responses = {}
        self.signals = []
        self.first = 0
        self.first_flag = True        

    def analysis(self, packet):

        if self.first_flag:
            self.first = packet.time
            self.first_flag = False

        if "ICMP" in packet:
            pkt = packet["ICMP"]

            if pkt.type == 8:
                self.responses[pkt.seq] = packet.time - self.first

            elif (pkt.type == 0) and (pkt.seq in self.responses):
                del self.responses[pkt.seq]

            #print(str(packet["ICMP"].seq) + " " + str(packet["ICMP"].type))    

        if "UDP" in packet:
            if "test" in str(packet["UDP"].payload):
                self.signals.append(packet.time - self.first)
                #print('{0:.11}'.format(packet.time)[:-5])

    def analyze(self):
        sniff(offline=self.pcap_name,prn=self.analysis,store=0)

if __name__ == '__main__':
    a = analyzer(sys.argv[1])
    a.analyze()
    print(str(a.__dict__))
