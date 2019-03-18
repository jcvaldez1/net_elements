import socket
import subprocess
import ast
import matplotlib.pyplot as plt
import json
import sys



def gen_input(tuple_list):
    x = []
    y = []

    for theTuple in tuple_list:
        x.append(theTuple[0])
        y.append(theTuple[2])

    return x,y


f = open("500packets.txt", "r")
list_packets_new = f.read()
splitted = list_packets_new.split('$')
GENresponseDistrib   = ast.literal_eval(splitted[0])
GENrequestDistrib    = ast.literal_eval(splitted[1])
GENdelayDistrib      = ast.literal_eval(splitted[2])

f = open("synthetic500.txt", "r")
list_packets_new = f.read()
splitted = list_packets_new.split('$')
SYNresponseDistrib   = ast.literal_eval(splitted[0])
SYNrequestDistrib    = ast.literal_eval(splitted[1])
SYNdelayDistrib      = ast.literal_eval(splitted[2])



plt.figure(1)

plt.subplot(221)
x,y = gen_input( GENresponseDistrib)
plt.plot(x, y, 'b')
x,y = gen_input( SYNresponseDistrib)
plt.plot(x, y, 'r')
plt.yscale('linear')
plt.title('Response Size')
plt.grid(True)

plt.subplot(222)
x,y = gen_input( GENrequestDistrib)
plt.plot(x, y, 'b')
x,y = gen_input( SYNrequestDistrib)
plt.plot(x, y, 'r')
plt.yscale('linear')
plt.title('Request Size')
plt.grid(True)

plt.subplot(223)
x,y = gen_input( GENdelayDistrib)
plt.plot(x, y, 'b')
x,y = gen_input( SYNdelayDistrib)
plt.plot(x, y, 'r')
plt.yscale('linear')
plt.title('RTT')
plt.grid(True)

plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

plt.show()
