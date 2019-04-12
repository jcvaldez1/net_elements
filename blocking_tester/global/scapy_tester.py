from scapy.all import *
from scapy_http import http
from tldextract import *


def anal(packet):
    FIN = 0x01
    ACK = 0x10
    if packet.haslayer(TCP):
        if (packet["TCP"].flags & FIN) and (packet["TCP"].flags & ACK) and (packet["IP"].src == "10.147.4.52"):
            #print(packet.payload)
            packet.show()
            pass
    else:
        pass

def sniffe():
    sniff(offline="block_trace.pcap",prn=anal,store=0)


if __name__ == "__main__":
    sniffe()
