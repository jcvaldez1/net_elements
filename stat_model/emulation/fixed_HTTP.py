import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random
import constants

class packet_analyzer:


    def __init__(self):
        self.PCAP_NAME = "merged10.147.80.139.pcap"
        self.globalcounter = 0
        self.subnet = '10.147.80'
        self.totalWaitTime = 0
        self.requestNumber = 0
        self.total_client_packets = 0
        self.requestNumberResponded = 0
        self.total_packets = 0
        self.currentConnections = dict()
        self.currentConnectionsTCP = dict()
        self.TCPrequestDistribution = dict()
        self.TCPresponseDistribution = dict()
        self.TCPdelayDistribution = dict()
        self.TCPDestinationDistribution = dict()
        self.HTTPrequestDistribution = dict()
        self.HTTPresponseDistribution = dict()
        self.HTTPdelayDistribution = dict()
        self.HTTPDestinationDistribution = dict()
        self.HTTPsourceDistribution = dict()
        self.TCPsourceDistribution = dict()
        self.messageTypeDistribution = []
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
        self.HTTPrequestPayloadOutlier = 0
        self.HTTPresponsePayloadOutlier = 0
        self.HTTPdelayOutlier = 0

        self.splitter = 10000
        self.newIPs = self.createIPs(100)
        self.connection_lengths = dict()
        pass

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
    def initDicts(self, increment, count, starting):
        theDict = dict()
        counter = 0
        x = starting
        y = increment + starting
        while counter < count:
            counter = counter + 1
            theDict[(x,y)] = 0
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
    def transformIntoCumulative(self, origDict):
        theDict, total = self.cleanDicts(origDict)
        previousValue = 0
        newReturn = []
        concrete_value = 0

        # decimal_returner would be used to project concrete_value
        # back into 0 < concrete_value < 1 constraints
        decimal_returner = 1.0/self.splitter

        for key in theDict:
            # this basically truncates all significant figures
            # below the threshold defined by splitter from
            # the probability value taken from theDict
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

            #if("HTTP Request" in packet):
            #    # print("Request in")
            #    total_client_packets = total_client_packets + 1

            #    currentConnections[(theIP.dst ,theTCP.sport , len(packet["TCP"].payload)+packet["TCP"].seq) ] = packet.time
            #    requestNumber = requestNumber + 1
            #    
            #    HTTPrequestPayloadOutlier = HTTPrequestPayloadOutlier + dictClassifier(len(packet["TCP"].payload),HTTPrequestDistribution)
            #    HTTPsourceDistribution.setdefault(theIP.src,0)
            #    HTTPsourceDistribution[theIP.src] = HTTPsourceDistribution[theIP.src] + 1
            #    if (theIP.src,theIP.dst) in HTTPDestinationDistribution:
            #        HTTPDestinationDistribution[(theIP.src,theIP.dst)] = HTTPDestinationDistribution[(theIP.src,theIP.dst)] + 1
            #    else:
            #        HTTPDestinationDistribution[(theIP.src,theIP.dst)] = 0
            #elif("HTTP Response" in packet):
            #    # print("Response in")
            #    if( (theIP.src, theTCP.dport, theTCP.ack) in currentConnections ):
            #        totalWaitTime = totalWaitTime + packet.time - currentConnections[(theIP.src, theTCP.dport, theTCP.ack)]
            #        requestNumberResponded = requestNumberResponded + 1

            #        HTTPdelayOutlier = HTTPdelayOutlier + dictClassifier(packet.time - currentConnections[(theIP.src, theTCP.dport, theTCP.ack)],HTTPdelayDistribution)
            #        HTTPresponsePayloadOutlier = HTTPresponsePayloadOutlier + dictClassifier(len(packet["TCP"].payload),HTTPresponseDistribution)
            #        
            #        del currentConnections[(theIP.src, theTCP.dport, theTCP.ack)]
            # TCP HANDLER


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
                    if(not theIP.dst.startswith(self.subnet)):
                        self.total_client_packets = self.total_client_packets + 1
                        self.TCPsourceDistribution.setdefault(theIP.src,0)
                        self.TCPsourceDistribution[theIP.src] = self.TCPsourceDistribution[theIP.src] + 1
                        if (theIP.src,theIP.dst) in self.TCPDestinationDistribution:
                            self.TCPDestinationDistribution[(theIP.src,theIP.dst)] = self.TCPDestinationDistribution[(theIP.src,theIP.dst)] + 1
                        else:
                            self.TCPDestinationDistribution[(theIP.src,theIP.dst)] = 0
                # else:
                    # globalcounter = globalcounter + 1	
            # else:
            # 	globalcounter = globalcounter + 1

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

            # THE FOLLOWING BLOCK WOULD PICK A RANDOM NUMBER
            # TO CHOOSE A SELECTED ENTRY FROM THE CUMULATIVE DISTRIBUTION
            # SELECT RANDOM NUMBER
            #rando_num = random.random()
            #realOGTuple = ()
            #for theTuple in messageTypeDistribution:
            #    realOGTuple = theTuple
            #    if(rando_num <= theTuple[1]):
            #        break

            # x = realOGTuple[0]
            # NOTE HTTP ELIMINATED FOR SIMPLICITY
            #if(x == "HTTP"):
            #    theRequests.append( ("HTTP", generatePacketValue(HTTPrequestDistribution), 
            #                                 generatePacketValue(HTTPdelayDistribution) , 
            #                                 generatePacketValue(HTTPresponseDistribution) , 
            #                                 generateDestination(HTTPsourceDistribution,HTTPDestinationDistribution),0 
            #                                 ) 
            #    )
            #if(x == "TCP"):

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

        self.TCPrequestDistribution = self.initDicts(100,1000,0)
        self.TCPresponseDistribution = self.initDicts(100,1000,0)
        self.TCPdelayDistribution = self.initDicts(0.005,10000,0)

        #self.HTTPrequestDistribution = self.initDicts(100,1000,0)
        #self.HTTPresponseDistribution = self.initDicts(100,1000,0)
        #self.HTTPdelayDistribution = self.initDicts(0.005,10000,0)

        sniff(offline=self.PCAP_NAME,prn=self.analysis,store=0)

        # self.messageTypeDistribution = [ ("HTTP" , (requestNumber*1.0/(rawTCPNumber+requestNumber))) , ("TCP" , (rawTCPNumber*1.0/(rawTCPNumber+requestNumber))) ]
        # ADJUST FOR TCP ONLY FOR NOW
        self.messageTypeDistribution = [ ("HTTP" , 0) , ("TCP" , 1) ]
        
        #self.TCPresponseDistribution, total = self.cleanDicts(self.TCPresponseDistribution)	
        #self.TCPresponseDistribution = self.transformIntoCumulative(self.TCPresponseDistribution,total)
        #print(str(self.TCPresponseDistribution))
        self.TCPresponseDistribution = self.transformIntoCumulative(self.TCPresponseDistribution)


        #self.TCPrequestDistribution, total = self.cleanDicts(self.TCPrequestDistribution)
        #self.TCPrequestDistribution = self.transformIntoCumulative(TCPrequestDistribution,total)
        self.TCPrequestDistribution = self.transformIntoCumulative(self.TCPrequestDistribution)

        #self.HTTPrequestDistribution,total = cleanDicts(HTTPrequestDistribution)
        #self.HTTPrequestDistribution = transformIntoCumulative(HTTPrequestDistribution,total,splitter)
        #self.HTTPresponseDistribution,total = cleanDicts(HTTPresponseDistribution)
        #self.HTTPresponseDistribution = transformIntoCumulative(HTTPresponseDistribution,total,splitter)
        #self.HTTPdelayDistribution,total = cleanDicts(HTTPdelayDistribution)
        #self.HTTPdelayDistribution = transformIntoCumulative(HTTPdelayDistribution,total,splitter)

        #self.TCPdelayDistribution,total = self.cleanDicts(self.TCPdelayDistribution)
        #self.TCPdelayDistribution = self.transformIntoCumulative(self.TCPdelayDistribution,total,self.splitter)
        self.TCPdelayDistribution = self.transformIntoCumulative(self.TCPdelayDistribution)

        # print(str(HTTPDestinationDistribution))
        # print(str(TCPDestinationDistribution))
        #HTTPDestinationDistribution,total = cleanDicts(HTTPDestinationDistribution)
        #HTTPDestinationDistribution = transformIntoCumulative(HTTPDestinationDistribution,total,splitter)
        #self.HTTPDestinationDistribution = self.transformIntoCumulative(self.HTTPDestinationDistribution)

        #TCPDestinationDistribution,total = cleanDicts(TCPDestinationDistribution)
        #TCPDestinationDistribution = transformIntoCumulative(TCPDestinationDistribution,total,splitter)
        self.TCPDestinationDistribution = self.transformIntoCumulative(self.TCPDestinationDistribution)

        #HTTPsourceDistribution,total = cleanDicts(HTTPsourceDistribution)
        #HTTPsourceDistribution = transformIntoCumulative(HTTPsourceDistribution,total,splitter)
        # print(str(HTTPsourceDistribution))
        # HTTPsourceDistribution = newIPs
        #TCPsourceDistribution,total = cleanDicts(TCPsourceDistribution)
        #TCPsourceDistribution = transformIntoCumulative(TCPsourceDistribution,total,splitter)
        self.TCPsourceDistribution = self.transformIntoCumulative(self.TCPsourceDistribution)
        # print(str(TCPsourceDistribution))
        # TCPsourceDistribution = newIPs
        # for key in sourceDistribution:
        # 	sourceDistribution[key] = (sourceDistribution[key]*1.0)/total
        # print(connection_lengths)
        # print(globalcounter)
        # print(total_packets)
        # print(str(HTTPDestinationDistribution))
        # print(str(TCPDestinationDistribution))
        self.adjustConnectionLength()
        #total_packets = 100;
        #requests = generatePackets(messageTypeDistribution, 
        #                           HTTPdelayDistribution, TCPdelayDistribution, 
        #                           TCPresponseDistribution, TCPrequestDistribution, 
        #                           HTTPrequestDistribution, HTTPresponseDistribution, 
        #                           HTTPDestinationDistribution, TCPDestinationDistribution, 
        #                           HTTPsourceDistribution, TCPsourceDistribution,
        #                           total_packets,connection_lengths)
        requests = self.generatePackets()
        return requests



if __name__ == '__main__':
    # initEmulation(PCAP_NAME)

    print(str(packet_analyzer().initEmulation()))

    # print(str(initEmulation(PCAP_NAME)))
# return initEmulation(sys.argv[1])
# print(str(requests))
# print(str(responses))
# return requests, responses
# print(str(initEmulation(pcap_name)))
# total_packets = 10
# (0.025,0.6) are the error packets
# (0,0.025) is the main one, this is as small of an interval we should go due to convergence issues
# print(str(messageTypeDistribution))
# print("Total Request waiting time: " + str(totalWaitTime) +"s")
# print("Total responded HTTP requests: " + str(requestNumberResponded))
# print("Average response delay: " + str((totalWaitTime/(requestNumberResponded+rawTCPResponded)))+"s")
# print("Average response delay: " + str((totalWaitTime/(requestNumberResponded*1.0)))+"s")
# print("HTTP Request frequency: " + str(((requestNumber*1.0)/((lastTimeStamp - firstTimeStamp))*1.0)) + " requests/seconds")
# print("Overall Packets/s: " + str(total_packets*1.0/((lastTimeStamp - firstTimeStamp)*1.0)))
# print(str(TCPrequestDistribution))
# print(str(TCPresponseDistribution))
# print(str(requestPayloadOutlier))
# print(str(responsePayloadOutlier))
# print(str(HTTPresponseDistribution))
# print(str(HTTPrequestDistribution))
# print(str(HTTPresponsePayloadOutlier))
# print(str(HTTPrequestPayloadOutlier))
# print(str(HTTPdelayDistribution))
# print(str(TCPdelayDistribution))
# print(str(HTTPdelayOutlier))
# print(str(TCPdelayOutlier))
# print(str(requests))
# print(str(responses))
# print(len(str(requests)))
# print(len(str(responses)))
