import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random
import constants

class packet_analyzer:

    def __init__(self, pcap_name=constants.PCAP_FILE_NAME, subnet=constants.CLIENT_SUBNET,
    precision=constants.FLOAT_PRECISION):
        self.pcap_name = pcap_name
        self.subnet = subnet
        self.globalcounter = 0
        self.total_packets = 0
        self.currentConnectionsTCP = dict()
        TCPreqkeys   = []
        TCPrespkeys  = []
        TCPdelaykeys = []        
        self.TCPrequestDistribution = self.initDicts(constants.PAYLOAD_INTERVAL_SIZE,constants.PAYLOAD_INTERVAL_NUM,0,
        TCPreqkeys)
        self.TCPresponseDistribution = self.initDicts(constants.PAYLOAD_INTERVAL_SIZE,constants.PAYLOAD_INTERVAL_NUM,0,
        TCPrespkeys)
        self.TCPdelayDistribution = self.initDicts(constants.DELAY_INTERVAL_SIZE,constants.DELAY_INTERVAL_NUM,0,
        TCPdelaykeys)

        self.TCPreqkeys =   TCPreqkeys   
        self.TCPrespkeys =  TCPrespkeys  
        self.TCPdelaykeys = TCPdelaykeys 

        self.TCPDestinationDistribution = dict()
        self.TCPsourceDistribution = dict()
        self.firstTimeStamp = 0
        self.lastTimeStamp = 0 
        self.rawTCPNumber = 0
        self.rawTCPResponded = 0
        self.totalWaitTimeTCP = 0
        
        # CARDINALITY OF SINGULAR
        # OUTLIER VALUES BASED OFF
        # THE INTERVALS DEFINED BY
        # THE DATA STRUCTS
        self.TCPrequestPayloadOutlier = 0
        self.TCPresponsePayloadOutlier = 0
        self.TCPdelayOutlier = 0

        self.splitter = (10**precision)
        self.newIPs = self.createIPs(100)
        self.connection_lengths = dict()

    def checkForSYNACK(self, theIPsrc, theIPdst, theTCP):
        # DECLARE HEX FLAGS FOR CHECKING
        FIN = 0x01
        SYN = 0x02
        ACK = 0x10

        # MUST ASSUME THAT theIPsrc COMES FROM THE HOST SIDE OF THE NETWORK AND theIPdst COMES FROM THE OUTSIDE
        # print(theTCP.flags)
        # if (theTCP.flags & SYN) and (theTCP.flags & ACK):
        # 	print("theTCP")
        if (theIPsrc,theIPdst) in self.connection_lengths:
            # INCREASE PACKET COUNTER
            self.connection_lengths[(theIPsrc,theIPdst)][2] = self.connection_lengths[(theIPsrc,theIPdst)][2] + 1

            # CATCH SYN OR SYNACK
            FLAG = self.connection_lengths[(theIPsrc,theIPdst)][1]
            # print(FLAG)
            if theTCP.flags & SYN:
                # RIGHT TRACK; EXPECTING SYNACK AND RECEIVE SYNACK
                if (theTCP.flags & ACK) and (FLAG == 'SYNACK'):
                    # CHANGE EXPECTATION ON NEXT RECEIVE TO BE ACK
                    self.connection_lengths[(theIPsrc,theIPdst)][1] = 'ACK'
                # RECEIVE SYN ONLY NOT SYNACK AND MATCHES WITH EXPECTATION "SYN"
                elif FLAG == 'SYN':
                    self.connection_lengths[(theIPsrc,theIPdst)][1] = 'SYNACK'
            # CATCH ACK OR NORMAL TCP PACKET
            elif (theTCP.flags & ACK) and (FLAG == 'ACK'):
                # RESET TO SYN AND INCREMENT CONNECTION EST. COUNTER
                self.connection_lengths[(theIPsrc,theIPdst)][0] = self.connection_lengths[(theIPsrc,theIPdst)][0] + 1
                self.connection_lengths[(theIPsrc,theIPdst)][1] = 'SYN'	
        # NEW CONNECTION, MAKE NO ASSUMPTIONS; STICK TO PROTOCOL
        else:
            self.connection_lengths[(theIPsrc,theIPdst)] = [0,'SYN',1]
            if theTCP.flags & SYN:
                self.connection_lengths[(theIPsrc,theIPdst)] = [0,'SYNACK',1]


    def adjustConnectionLength(self):
        for x in self.connection_lengths:
            # NUMBER OF PACKETS src,dst pair ->  KEY = (IP.src,IP.dst)
            TOTAL_PACKETS = self.connection_lengths[x][2]
            # NUMBER OF THREE WAY HANDSHAKE TRIOS (CONNECTION INITIATIONS)
            CONNECTIONS_INITIATED = self.connection_lengths[x][0]
            # REWRITE self.connection_lengths
            self.connection_lengths[x] = [ TOTAL_PACKETS / CONNECTIONS_INITIATED , 0 ]
            # connection_lengths now effectively contains key -> value == (IP.src,IP.dst) ->  [PACKETS_PER_CONNECTION , 0]


    def createIPs(self, total):
        returnThis = []
        for x in range(0,total):
            returnThis.append(self.subnet + "."  + str(x))
        return returnThis


    # INITIALIZES THE DATA STRUCT FOR CONTAINING DISTRIBS
    def initDicts(self, increment, count, starting, keylist):
        theDict = dict()
        counter = 0
        x = starting
        y = increment + starting
        while counter < count:
            counter = counter + 1
            theDict[(x,y)] = 0
            keylist.append((x,y))
            x = x + increment
            y = y + increment
        return theDict

    # THIS FUNCTION BASICALLY RETURNS ALL INTERVALS
    # FROM THE DATA STRUCT THAT HAVE ENTRIES ON THEM
    # IT REMOVES ALL EMPTY INTERVALS
    # (INTERVALS THAT DO NOT HAVE ANY VALUES)
    def cleanDicts(self, hey):
        returnThis = 0
        newDict = dict()
        for key, value in hey.iteritems():
            if(value != 0):
                newDict[key] = value
                returnThis = returnThis + value
        return newDict,(returnThis*1.0)

    # JUST INCREMENTS COUNT WHEN theTime is INSIDE AN INTERVAL IN theDict
    def dictClassifier(self, theTime, theDict):
        flag = True
        for key in theDict:
            if(theTime >= key[0]) and (theTime < key[1]):
                theDict[key] = theDict[key] + 1
                flag = False
                break
        if flag:
            return 1
        return 0

    # THIS FUNCTION BASICALLY TRANSFORMS THE
    # INTERVAL DATA STRUCTURE INTO A CUMULATIVE
    # PROBABILITY DISTRIBUTION FUNCTION (VALUE SET)
    def transformIntoCumulative(self, origDict, orderer=None):
        theDict, total = self.cleanDicts(origDict)
        previousValue = 0
        newReturn = []
        concrete_value = 0

        # decimal_returner would be used to project concrete_value
        # back into 0 < concrete_value < 1 constraints
        decimal_returner = 1.0/self.splitter
        keys = []
        if orderer:
            keys=orderer
        else:
            keys=theDict
        for key in keys:
            # this basically truncates all significant figures
            # below the threshold defined by splitter from
            # the probability value taken from theDict
            if key in theDict:
                concrete_value = int(theDict[key]/total*self.splitter)
                if( concrete_value != 0 ):

                    # FIX THIS SHIT PLEASE
                    if len(key) == 2:
                        newReturn.append( ( key[0], key[1], previousValue + (concrete_value*decimal_returner) ) )
                    else:
                        newReturn.append( ( key, previousValue + (concrete_value*decimal_returner)))
                    previousValue = previousValue + (concrete_value*decimal_returner)

        return newReturn

    def analysis(self, packet):

        PSH = 0x08
        RST = 0x04

        if(self.firstTimeStamp > 0):
            self.lastTimeStamp = packet.time
        else:
            self.firstTimeStamp = packet.time
        
        if("TCP" in packet):
            self.total_packets = self.total_packets + 1
            theIP=packet["IP"]
            theTCP= packet["TCP"]

            # NOTE DATA STRUCTURE FOR PACKET DICTIONARY
            # (KEY) -> (VALUE)
            # (IP.src,IP.dst) -> (TIMESTAMP)
            if not(theTCP.flags & RST):
                self.globalcounter = self.globalcounter + 1
                # RESPONSE HANDLER
                if( (theIP.src, theTCP.dport) in self.currentConnectionsTCP ):
                    
                    # OUTLIER INCREMENTER, THE FOLLOWING COUNTERS ARE FOR TRACKING
                    # OUTLIER VALUES, AND WOULD BE A GUIDE FOR FIXING THE INCLUDED
                    # DATA INTERVALS
                    OUTLIER_FLAG = self.dictClassifier(packet.time - self.currentConnectionsTCP[(theIP.src, theTCP.dport)], self.TCPdelayDistribution)
                    self.TCPdelayOutlier = self.TCPdelayOutlier + OUTLIER_FLAG 

                    self.TCPresponsePayloadOutlier = self.TCPresponsePayloadOutlier + self.dictClassifier(len(packet["TCP"].payload), self.TCPresponseDistribution)
                    
                    # END OF OUTLIER INCREMENTING


                    # RETRIVES RTT FROM CLIENT SIDE BY FOLLOWING THIS FORMULA:
                    # RTT = (RESPONSE_ARRIVAL_TIMESTAMP) - (REQUEST_SEND_TIMESTAMP)
                    # THE VALUE IS THEN ADDED TOWARDS TOTAL WAIT TIME
                    if not OUTLIER_FLAG:
                        # NOTE -> OUTLIER VALUES ARE NOT GOING TO BE ADDED TO THE TOTAL WAITTIME
                        self.totalWaitTimeTCP = self.totalWaitTimeTCP + packet.time - self.currentConnectionsTCP[(theIP.src, theTCP.dport)]
                    
                    # INCREMENT PACKET COUNTER
                    self.rawTCPResponded = self.rawTCPResponded + 1
                            
                    # SUBMIT FOR FLAG EVALUATION (FOR CONNECTION ESTABLISHMENT CHECKING)
                    self.checkForSYNACK(theIP.dst, theIP.src, theTCP)
 
                    # del currentConnectionsTCP[(theIP.src, theTCP.dport, theTCP.ack)]
                    self.currentConnectionsTCP[(theIP.src, theTCP.dport)] = packet.time

                # REQUEST HANDLER
                elif (theIP.src.startswith(self.subnet)):
                    # RECORD TIMESTAMP FOR REQUEST PACKET
                    self.currentConnectionsTCP[(theIP.dst, theTCP.sport)] = packet.time
                    
                    # INCREMENT TCP PACKET COUNTER
                    self.rawTCPNumber = self.rawTCPNumber + 1

                    # SUBMIT FOR FLAG EVALUATION (FOR CONNECTION ESTABLISHMENT CHECKING)
                    self.checkForSYNACK(theIP.src, theIP.dst, theTCP)

                    # INCREMENTS OUTLIER COUNTER IF FOUND
                    self.TCPrequestPayloadOutlier = self.TCPrequestPayloadOutlier + self.dictClassifier(len(packet["TCP"].payload), self.TCPrequestDistribution)

                    # THE FOLLOWING BLOCK IS FOR CATCHING INCONSISTENCIES WITHIN THE SYSTEM
                    # IT CATCHES INTER-CLIENT COMMUNICATION PACKETS
                    # ( IP.src == client_subnet ) && (IP.dst == client_subnet)
                    
                    #if(not theIP.dst.startswith(self.subnet)):
                    if(True):
                        self.TCPsourceDistribution.setdefault(theIP.src,0)
                        self.TCPsourceDistribution[theIP.src] = self.TCPsourceDistribution[theIP.src] + 1
                        if (theIP.src,theIP.dst) in self.TCPDestinationDistribution:
                            self.TCPDestinationDistribution[(theIP.src,theIP.dst)] = self.TCPDestinationDistribution[(theIP.src,theIP.dst)] + 1
                        else:
                            self.TCPDestinationDistribution[(theIP.src,theIP.dst)] = 0

    def generatePacketValue(self, requestDistribution):
        # requestDistribution[x] = (0,n,probability)
        rando_num = random.random()
        realOGTuple = ()
        randfunc = random.randint
        if(isinstance(requestDistribution[0][1],float)):
            randfunc = random.uniform
        for theTuple in requestDistribution:
            realOGTuple = theTuple
            if(rando_num <= theTuple[2]):
                break
        return randfunc(realOGTuple[0],realOGTuple[1])

    def generateDestination(self, srcDist, dstDist):
        global newIPs
        rando_num = random.random()
        realOGTuple = ""
        for theTuple in dstDist:
            realOGTuple = theTuple
            if(rando_num <= theTuple[2]):
                break
        return (realOGTuple[0],realOGTuple[1])
        # USE THIS FOR MULTIPLE IPS
        # return (srcDist[int(len(srcDist)*rando_num)],realOGTuple[1])

    def generatePackets(self):	
        # messageTypeDistribution[x] = ( MESSAGE_TYPE, CUMULATIVE_DISTRIBUTION_VALUE)
        # theRequests SHOULD CONTAIN THE FOLLOWING:
        # ("TCP" , request_payload, RTT_delay, response_payload, (IP.src,IP.dst), teardown_flag)
        theRequests = []
        counter = 0
        terminator = 0
        while counter < self.total_packets:
            counter = counter + 1

            src_dst_pair = self.generateDestination(self.TCPsourceDistribution, self.TCPDestinationDistribution)
            # PUT TERMINATOR VALUE IF LAST PACKET IN ITS CONNECTION

            # connection_lengths[0] => NUMBER OF PACKETS PER IP.src,IP.dst PAIR CONNECTION
            # connection_lengths[1] => NUMBER OF PACKETS SENT

            if(self.connection_lengths[src_dst_pair][1] % self.connection_lengths[src_dst_pair][0] == 0) and (self.connection_lengths[src_dst_pair][1] >= self.connection_lengths[src_dst_pair][0]):
                terminator = 1
            else:
                terminator = 0
            self.connection_lengths[src_dst_pair][1] = self.connection_lengths[src_dst_pair][1] + 1
            theRequests.append( ("TCP", self.generatePacketValue(self.TCPrequestDistribution), 
                                        self.generatePacketValue(self.TCPdelayDistribution), 
                                        self.generatePacketValue(self.TCPresponseDistribution), 
                                        src_dst_pair,
                                        terminator
                                        ) 
            )  
        return theRequests

    def initEmulation(self):
        sniff(offline=self.pcap_name,prn=self.analysis,store=0)
        self.TCPresponseDistribution = self.transformIntoCumulative(self.TCPresponseDistribution,self.TCPrespkeys)
        self.TCPrequestDistribution = self.transformIntoCumulative(self.TCPrequestDistribution, self.TCPreqkeys)
        self.TCPdelayDistribution = self.transformIntoCumulative(self.TCPdelayDistribution,self.TCPdelaykeys)
        self.TCPDestinationDistribution = self.transformIntoCumulative(self.TCPDestinationDistribution)
        self.TCPsourceDistribution = self.transformIntoCumulative(self.TCPsourceDistribution)
        self.adjustConnectionLength()
        #print(str(self.TCPresponseDistribution))
        #print(str(self.TCPrequestDistribution))
        #print(str(self.TCPdelayDistribution))
        #print(str(self.TCPDestinationDistribution))
        #print(str(self.TCPsourceDistribution))
        #print(str(self.adjustConnectionLength))
        #requests = self.generatePackets()
        return requests



if __name__ == '__main__':
    a = packet_analyzer(sys.argv[1])
    print(str(a.initEmulation()))
    #print(str(a.TCPresponseDistribution))
    #print(str(a.TCPrequestDistribution))
    #print(str(a.TCPdelayDistribution))
