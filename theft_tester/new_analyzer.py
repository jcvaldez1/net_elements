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
        self.global_req = args.globals
        self.poll_req = args.pollreq
        self.poll_res = args.pollres
        self.countdown = open(args.countdown, "r")
        self.tests = 0

        # set time_stamp vars
        self.globalreq_timestamp = None
        self.pollreq_timestamp = None
        self.pollres_timestamp = None
        self.countdown_timestamp = None

        self.global_delay = 0
        self.poll_delay = 0
        self.controller_processing_time = 0

        self.sum = 0

    def analyze(self):

        f = open(self.poll_res,"r")
        prev_time = None
        flagge = True
        for line in f:
            temp_time = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
            if (temp_time > self.countdown_timestamp):
                if not prev_time:
                    prev_time = temp_time
                self.pollres_timestamp = prev_time
                flagge = False
                break
            prev_time = temp_time
        f.close()
        if flagge:
            self.pollres_timestamp = prev_time

        f = open(self.poll_req,"r")
        prev_time = None
        flagge = True
        for line in f:
            temp_time = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
            if (temp_time > self.pollres_timestamp):
                if not prev_time:
                    prev_time = temp_time
                self.pollreq_timestamp = prev_time
                flagge = False
                break
            prev_time = temp_time
        f.close()
        if flagge:
            self.pollreq_timestamp = prev_time

        f = open(self.global_req,"r")
        prev_time = None
        flagge = True
        for line in f:
            temp_time = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
            if (temp_time > self.pollreq_timestamp):
                if not prev_time:
                    prev_time = temp_time
                self.globalreq_timestamp = prev_time
                flagge = False
                break
            prev_time = temp_time
        f.close()
        if flagge:
            self.globalreq_timestamp = prev_time

        #print(str((self.pollreq_timestamp -
        #                      self.globalreq_timestamp).total_seconds()))
        self.global_delay += (self.pollreq_timestamp -
                              self.globalreq_timestamp).total_seconds()
        self.poll_delay += (self.pollres_timestamp -
                            self.pollreq_timestamp).total_seconds()

        self.controller_processing_time += (self.countdown_timestamp -
                                            self.pollres_timestamp
                                            ).total_seconds()
        self.tests += 1

    def sniffer(self): 

        for line in self.countdown:
            self.countdown_timestamp = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
            self.analyze()

        self.tests = float(self.tests)
        self.poll_delay /= self.tests
        self.controller_processing_time /= self.tests
        self.global_delay /= self.tests
        self.sum = self.poll_delay + self.controller_processing_time + self.global_delay
        print(str(self.global_delay))
        print(str(self.poll_delay))
        print(str(self.controller_processing_time))
        self.graph_gen()

    def graph_gen(self):
        labels = 'Poll Response Time', 'Controller Processing', 'Global controller request delay'
        sizes = [self.poll_delay/self.sum,
                 self.controller_processing_time/self.sum,
                 self.global_delay/self.sum]
        colors = ['gold','lightcoral','green']

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
        plt.axis('equal')
        plt.show()

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--globals', help='global requests file')
    parser.add_argument('--pollreq', help='poll requests file')
    parser.add_argument('--pollres', help='poll responses file')
    parser.add_argument('--countdown', help='countdown file')
    args=parser.parse_args()
    a = data_analyzer(args)
    a.sniffer()
    pass

