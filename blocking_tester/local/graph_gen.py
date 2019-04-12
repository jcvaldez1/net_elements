import socket
import subprocess
import ast
import matplotlib.pyplot as plt
import json
import sys

def graph():

    f = open(sys.argv[1], "r")
    list_packets_new = f.read()
    the_dict = ast.literal_eval(list_packets_new)

    #splitted = list_packets_new.split('$')
    signals    = the_dict['signals']
    #print(signals)
    throughput = the_dict['throughput']
    #print(throughput)
    keys = the_dict['key_order']
    #print(keys)
    
    #l = open(sys.argv[2], "w")
    #l.write(latex_gen(throughput))
    print(signalize(signals))
    plt.figure(1)
    
    plt.subplot(221)
    x,y = tupleize(throughput,keys)
    plt.plot(x, y, 'b')
    plt.title('Throughput')
    plt.grid(True)

    plt.show()

def latex_gen(params):
    
    the_string = "throughput\nx y\n0 0\n"
    x,y = tupleize(params)
    for index in range(0,len(x)):
        string = string + str(x[index]) + " " + y[index] + "\n"
    return the_string

def tupleize(data,key_order):

    x = []
    y = []
    prev = [-1,-1]
    current = -1
    flaggo = False
    if isinstance(data,list):
        for d in data:
            x.append(d)
            y.append(0)
            x.append(d)
            y.append(50)

    else:
    
        for key in key_order:
            x.append(key/1000)
            if key in data:
                y.append(data[key])
                current = data[key]
            else:
                y.append(0)
                current = 0
            if (flaggo) and (prev[1] == current) and (key != key_order[-1]):
                x.pop()
                y.pop()
            elif (flaggo) and (prev[1] != current):
                # append at prev index
                x = x[:-1] + [prev[0]] + x[-1:]
                y = y[:-1] + [prev[1]] + y[-1:]
            else:
                flaggo = True
            prev[0] = key/1000
            prev[1] = current
    
    the_string = "throughput\nx y\n0 0\n"
    for index in range(0,len(x)):
        the_string = the_string + str(x[index]) + " "+ str(y[index]) + "\n"
    
    print(the_string)
    return x,y
    
def signalize(signals):

    the_string = "signals\nx y\n"
    for sig in signals:
        the_string = the_string + str(sig/1000) + " 0\n" + str(sig/1000) + " 60\n"
    
    return the_string
        

if __name__ == "__main__":
    graph()
