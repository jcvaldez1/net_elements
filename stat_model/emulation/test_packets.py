import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from scapy_http import http
from tldextract import *
import math
import random

def swap(x,y):
	return y,x

def checkForSYNACK(theIPsrc,theIPdst,theTCP,connection_lengths):
	# DECLARE HEX FLAGS FOR CHECKING
	FIN = 0x01
	SYN = 0x02
	ACK = 0x10

	# MUST ASSUME THAT theIPsrc COMES FROM THE HOST SIDE OF THE NETWORK AND theIPdst COMES FROM THE OUTSIDE
	# print(theTCP.flags)
	# if (theTCP.flags & SYN) and (theTCP.flags & ACK):
	# 	print("theTCP")
	if (theIPsrc,theIPdst) in connection_lengths:
		# INCREASE PACKET COUNTER
		connection_lengths[(theIPsrc,theIPdst)][2] = connection_lengths[(theIPsrc,theIPdst)][2] + 1

		# CATCH SYN OR SYNACK
		FLAG = connection_lengths[(theIPsrc,theIPdst)][1]
		# print(FLAG)
		if theTCP.flags & SYN:
			# RIGHT TRACK; EXPECTING SYNACK AND RECEIVE SYNACK
			if (theTCP.flags & ACK) and (FLAG == 'SYNACK'):
				# CHANGE EXPECTATION ON NEXT RECEIVE TO BE ACK
				connection_lengths[(theIPsrc,theIPdst)][1] = 'ACK'
			# RECEIVE SYN ONLY NOT SYNACK AND MATCHES WITH EXPECTATION "SYN"
			elif FLAG == 'SYN':
				connection_lengths[(theIPsrc,theIPdst)][1] = 'SYNACK'
		# CATCH ACK OR NORMAL TCP PACKET
		elif (theTCP.flags & ACK) and (FLAG == 'ACK'):
			# RESET TO SYN AND INCREMENT CONNECTION EST. COUNTER
			connection_lengths[(theIPsrc,theIPdst)][0] = connection_lengths[(theIPsrc,theIPdst)][0] + 1
			connection_lengths[(theIPsrc,theIPdst)][1] = 'SYN'	
	# NEW CONNECTION, MAKE NO ASSUMPTIONS; STICK TO PROTOCOL
	else:
		connection_lengths[(theIPsrc,theIPdst)] = [0,'SYN',1]
		if theTCP.flags & SYN:
			connection_lengths[(theIPsrc,theIPdst)] = [0,'SYNACK',1]

def adjustConnectionLength(connection_lengths, globalpacketcount):
	for x in connection_lengths:
		# NOW CONNECTION LENGTHS CONTAINS (KEY)(SRC,DST) = (VAL) (PACKETS PER CONNECTION)
		#print(connection_lengths)
		connection_lengths[x] = [connection_lengths[x][2] / connection_lengths[x][0] , 0]


def createIPs(total):
	returnThis = []
	for x in range(0,total):
		returnThis.append(subnet + "."  + str(x))
	return returnThis


def initDicts(increment,count,starting):
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

def cleanDicts(hey):
	returnThis = 0
	newDict = dict()
	for x in hey:
		if(hey[x] != 0):
			newDict[x] = hey[x]
			returnThis = returnThis + hey[x]
	return newDict,(returnThis*1.0)

def dictClassifier(theTime,theDict):
	flag = True
	for key in theDict:
		if(theTime >= key[0]) and (theTime < key[1]):
			theDict[key] = theDict[key] + 1
			flag = False
			break
	if flag:
		return 1
	else:
		return 0

def transformIntoCumulative(theDict,total,splitter):
	previousValue = 0
	newReturn = []
	for key in theDict:
		if(int(theDict[key]/total*splitter) != 0):
			if len(key) == 2:
				newReturn.append((key[0],key[1],previousValue + (int(theDict[key]/total*splitter)*(1.0/splitter))))
			else:
				newReturn.append((key,previousValue + (int(theDict[key]/total*splitter)*(1.0/splitter))))
			previousValue = previousValue + (int(theDict[key]/total*splitter)*(1.0/splitter))
	return newReturn

def generatePacketValue(requestDistribution):
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

def generateDestination(srcDist,destDist):
	global newIPs
	rando_num = random.random()
	realOGTuple = ""
	for theTuple in destDist:
		realOGTuple = theTuple
		if(rando_num <= theTuple[2]):
			break
	return (realOGTuple[0],realOGTuple[1])
	# USE THIS FOR MULTIPLE IPS
	# return (srcDist[int(len(srcDist)*rando_num)],realOGTuple[1])

def generatePackets(messageTypeDistribution, HTTPdelayDistribution, TCPdelayDistribution, 
	                                         TCPresponseDistribution, TCPrequestDistribution, 
                                             HTTPrequestDistribution, HTTPresponseDistribution, 
                                             HTTPDestinationDistribution, TCPDestinationDistribution, 
                                             HTTPsourceDistribution , TCPsourceDistribution,
                                             totalPackets, connectionLengths):	
	# messageTypeDistribution[x] = ( MESSAGE_TYPE, CUMULATIVE_DISTRIBUTION_VALUE)
	theRequests = []
	counter = 0
	terminator = 0
	while counter < totalPackets:
		counter = counter + 1

		rando_num = random.random()
		realOGTuple = ()
		for theTuple in messageTypeDistribution:
			realOGTuple = theTuple
			if(rando_num <= theTuple[1]):
				break

		x = realOGTuple[0]
		if(x == "HTTP"):
			theRequests.append( ("HTTP", generatePacketValue(HTTPrequestDistribution), 
                                         generatePacketValue(HTTPdelayDistribution) , 
                                         generatePacketValue(HTTPresponseDistribution) , 
                                         generateDestination(HTTPsourceDistribution,HTTPDestinationDistribution),0 
                                         ) 
			)
		elif(x == "TCP"):
			temp = generateDestination(TCPsourceDistribution,TCPDestinationDistribution)
			# PUT TERMINATOR VALUE IF LAST PACKET IN ITS CONNECTION
			if(connectionLengths[temp][1] % connectionLengths[temp][0] == 0) and (connectionLengths[temp][1] >= connectionLengths[temp][0]):
				terminator = 1
			else:
				terminator = 0
			connectionLengths[temp][1] = connectionLengths[temp][1] + 1
			theRequests.append( ("TCP", generatePacketValue(TCPrequestDistribution), 
                                        generatePacketValue(TCPdelayDistribution), 
                                        generatePacketValue(TCPresponseDistribution) , 
                                        temp,
                                        terminator
                                        ) 
			)  
		# elif(x == "UDP"):
	return theRequests

def analysis(packet):

	global HTTPdelayDistribution
	global HTTPresponseDistribution
	global HTTPrequestDistribution
	global TCPrequestDistribution
	global TCPresponseDistribution
	global TCPdelayDistribution
	global TCPdelayOutlier
	global HTTPdelayOutlier
	global totalWaitTime
	global requestNumber
	global requestNumberResponded
	global total_packets
	global firstTimeStamp
	global lastTimeStamp
	global rawTCPNumber
	global rawTCPResponded
	global totalWaitTimeTCP
	global HTTPresponsePayloadOutlier
	global HTTPrequestPayloadOutlier
	global TCPrequestPayloadOutlier
	global TCPresponsePayloadOutlier
	global HTTPDestinationDistribution
	global TCPDestinationDistribution
	global subnet
	global total_client_packets
	global HTTPsourceDistribution
	global TCPsourceDistribution
	global connection_lengths
	global globalcounter
	PSH = 0x08
	RST = 0x04
	if(firstTimeStamp > 0):
		lastTimeStamp = packet.time
	else:
		firstTimeStamp = packet.time
	
	if("TCP" in packet):
		total_packets = total_packets + 1
		theIP=packet["IP"]
		theTCP= packet["TCP"]

		if("HTTP Request" in packet):
			# print("Request in")
			total_client_packets = total_client_packets + 1

			currentConnections[(theIP.dst ,theTCP.sport , len(packet["TCP"].payload)+packet["TCP"].seq) ] = packet.time
			requestNumber = requestNumber + 1
			
			HTTPrequestPayloadOutlier = HTTPrequestPayloadOutlier + dictClassifier(len(packet["TCP"].payload),HTTPrequestDistribution)
			HTTPsourceDistribution.setdefault(theIP.src,0)
			HTTPsourceDistribution[theIP.src] = HTTPsourceDistribution[theIP.src] + 1
			if (theIP.src,theIP.dst) in HTTPDestinationDistribution:
				HTTPDestinationDistribution[(theIP.src,theIP.dst)] = HTTPDestinationDistribution[(theIP.src,theIP.dst)] + 1
			else:
				HTTPDestinationDistribution[(theIP.src,theIP.dst)] = 0
		elif("HTTP Response" in packet):
			# print("Response in")
			if( (theIP.src, theTCP.dport, theTCP.ack) in currentConnections ):
				totalWaitTime = totalWaitTime + packet.time - currentConnections[(theIP.src, theTCP.dport, theTCP.ack)]
				requestNumberResponded = requestNumberResponded + 1

				HTTPdelayOutlier = HTTPdelayOutlier + dictClassifier(packet.time - currentConnections[(theIP.src, theTCP.dport, theTCP.ack)],HTTPdelayDistribution)
				HTTPresponsePayloadOutlier = HTTPresponsePayloadOutlier + dictClassifier(len(packet["TCP"].payload),HTTPresponseDistribution)
				
				del currentConnections[(theIP.src, theTCP.dport, theTCP.ack)]
		# TCP HANDLER
		elif not(theTCP.flags & RST):
			globalcounter = globalcounter + 1
			# RESPONSE HANDLER
			if( (theIP.src, theTCP.dport) in currentConnectionsTCP ):
				totalWaitTimeTCP = totalWaitTimeTCP + packet.time - currentConnectionsTCP[(theIP.src, theTCP.dport)]
				
				rawTCPResponded = rawTCPResponded + 1
						
				# print("could be here")		
				# SUBMIT FOR FLAG EVALUATION (FOR CONNECTION ESTABLISHMENT CHECKING)
				checkForSYNACK(theIP.dst,theIP.src,theTCP,connection_lengths)

				TCPdelayOutlier = TCPdelayOutlier +  dictClassifier(packet.time - currentConnectionsTCP[(theIP.src, theTCP.dport)],TCPdelayDistribution)
				TCPresponsePayloadOutlier = TCPresponsePayloadOutlier + dictClassifier(len(packet["TCP"].payload),TCPresponseDistribution)
				
				# del currentConnectionsTCP[(theIP.src, theTCP.dport, theTCP.ack)]
				currentConnectionsTCP[(theIP.src, theTCP.dport)] = packet.time

			# REQUEST HANDLER
			elif (theIP.src.startswith(subnet)):
				currentConnectionsTCP[(theIP.dst, theTCP.sport)] = packet.time
				
				rawTCPNumber = rawTCPNumber + 1

				# print("or here")
				# SUBMIT FOR FLAG EVALUATION (FOR CONNECTION ESTABLISHMENT CHECKING)
				checkForSYNACK(theIP.src,theIP.dst,theTCP,connection_lengths)

				TCPrequestPayloadOutlier = TCPrequestPayloadOutlier + dictClassifier(len(packet["TCP"].payload),TCPrequestDistribution)

				if(not theIP.dst.startswith(subnet)):
					total_client_packets = total_client_packets + 1
					TCPsourceDistribution.setdefault(theIP.src,0)
					TCPsourceDistribution[theIP.src] = TCPsourceDistribution[theIP.src] + 1
					if (theIP.src,theIP.dst) in TCPDestinationDistribution:
						TCPDestinationDistribution[(theIP.src,theIP.dst)] = TCPDestinationDistribution[(theIP.src,theIP.dst)] + 1
					else:
						TCPDestinationDistribution[(theIP.src,theIP.dst)] = 0
			# else:
				# globalcounter = globalcounter + 1	
		# else:
		# 	globalcounter = globalcounter + 1
def initEmulation(PCAP_NAME):

	global TCPrequestDistribution
	global TCPresponseDistribution
	global TCPdelayDistribution
	global HTTPrequestDistribution
	global HTTPresponseDistribution
	global HTTPdelayDistribution
	global rawTCPNumber
	global requestNumber
	global splitter
	global total_packets
	global HTTPDestinationDistribution
	global TCPDestinationDistribution
	global HTTPsourceDistribution
	global TCPsourceDistribution
	global total_client_packets
	global newIPs
	global globalcounter
	global connection_lengths
	TCPrequestDistribution = initDicts(100,1000,0)
	TCPresponseDistribution = initDicts(100,1000,0)
	TCPdelayDistribution = initDicts(0.005,10000,0)

	HTTPrequestDistribution = initDicts(100,1000,0)
	HTTPresponseDistribution = initDicts(100,1000,0)
	HTTPdelayDistribution = initDicts(0.005,10000,0)

	sniff(offline=PCAP_NAME,prn=analysis,store=0)

	messageTypeDistribution = [ ("HTTP" , (requestNumber*1.0/(rawTCPNumber+requestNumber))) , ("TCP" , (rawTCPNumber*1.0/(rawTCPNumber+requestNumber))) ]
	
	TCPresponseDistribution,total = cleanDicts(TCPresponseDistribution)	
	TCPresponseDistribution = transformIntoCumulative(TCPresponseDistribution,total,splitter)

	TCPrequestDistribution,total = cleanDicts(TCPrequestDistribution)
	TCPrequestDistribution = transformIntoCumulative(TCPrequestDistribution,total,splitter)

	HTTPrequestDistribution,total = cleanDicts(HTTPrequestDistribution)
	HTTPrequestDistribution = transformIntoCumulative(HTTPrequestDistribution,total,splitter)

	HTTPresponseDistribution,total = cleanDicts(HTTPresponseDistribution)
	HTTPresponseDistribution = transformIntoCumulative(HTTPresponseDistribution,total,splitter)

	HTTPdelayDistribution,total = cleanDicts(HTTPdelayDistribution)
	HTTPdelayDistribution = transformIntoCumulative(HTTPdelayDistribution,total,splitter)

	TCPdelayDistribution,total = cleanDicts(TCPdelayDistribution)
	TCPdelayDistribution = transformIntoCumulative(TCPdelayDistribution,total,splitter)
	# print(str(HTTPDestinationDistribution))
	# print(str(TCPDestinationDistribution))
	HTTPDestinationDistribution,total = cleanDicts(HTTPDestinationDistribution)
	HTTPDestinationDistribution = transformIntoCumulative(HTTPDestinationDistribution,total,splitter)

	TCPDestinationDistribution,total = cleanDicts(TCPDestinationDistribution)
	TCPDestinationDistribution = transformIntoCumulative(TCPDestinationDistribution,total,splitter)

	HTTPsourceDistribution,total = cleanDicts(HTTPsourceDistribution)
	HTTPsourceDistribution = transformIntoCumulative(HTTPsourceDistribution,total,splitter)
	# print(str(HTTPsourceDistribution))
	# HTTPsourceDistribution = newIPs
	TCPsourceDistribution,total = cleanDicts(TCPsourceDistribution)
	TCPsourceDistribution = transformIntoCumulative(TCPsourceDistribution,total,splitter)
	# print(str(TCPsourceDistribution))
	# TCPsourceDistribution = newIPs
	# for key in sourceDistribution:
	# 	sourceDistribution[key] = (sourceDistribution[key]*1.0)/total
	# print(connection_lengths)
	# print(globalcounter)
	# print(total_packets)
	# print(str(HTTPDestinationDistribution))
	# print(str(TCPDestinationDistribution))
	adjustConnectionLength(connection_lengths, globalcounter)
	total_packets = 100;
	requests = generatePackets(messageTypeDistribution, 
                               HTTPdelayDistribution, TCPdelayDistribution, 
                               TCPresponseDistribution, TCPrequestDistribution, 
                               HTTPrequestDistribution, HTTPresponseDistribution, 
                               HTTPDestinationDistribution, TCPDestinationDistribution, 
                               HTTPsourceDistribution, TCPsourceDistribution,
                               total_packets,connection_lengths)

	return requests


PCAP_NAME = "merged10.147.80.139.pcap"
#PCAP_NAME = "small3.pcap"
# PCAP_NAME = "testing.pcap"
globalcounter = 0
subnet = '10.147.80'
totalWaitTime = 0
requestNumber = 0
total_client_packets = 0
requestNumberResponded = 0
total_packets = 0
currentConnections = dict()
currentConnectionsTCP = dict()
TCPrequestDistribution = dict()
TCPresponseDistribution = dict()
TCPdelayDistribution = dict()
TCPDestinationDistribution = dict()
HTTPrequestDistribution = dict()
HTTPresponseDistribution = dict()
HTTPdelayDistribution = dict()
HTTPDestinationDistribution = dict()
HTTPsourceDistribution = dict()
TCPsourceDistribution = dict()
messageTypeDistribution = []
firstTimeStamp = 0
lastTimeStamp = 0 
rawTCPNumber = 0
rawTCPResponded = 0
totalWaitTimeTCP = 0
TCPrequestPayloadOutlier = 0
TCPresponsePayloadOutlier = 0
TCPdelayOutlier = 0
HTTPrequestPayloadOutlier = 0
HTTPresponsePayloadOutlier = 0
HTTPdelayOutlier = 0
splitter = 10000
newIPs = createIPs(100)

connection_lengths = dict()

if __name__ == '__main__':
	# initEmulation(PCAP_NAME)
	print(str(initEmulation(PCAP_NAME)))
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
