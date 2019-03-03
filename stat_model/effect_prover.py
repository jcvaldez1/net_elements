import socket
import subprocess
import ast
import matplotlib.pyplot as plt

class clone:
    
    def __init__(self):
        
        # run proxy for converting py2 to py3
        python_command = ['python' ,'proxy_parser.py']
        proc = subprocess.Popen(python_command,stdout=subprocess.PIPE)
        list_packets = proc.stdout.read()
        list_packets = list_packets.decode()
        list_packets_new = list_packets[:len(list_packets)-1]
        splitted = list_packets_new.split('$')

        # declare the metrics
        self.responseDistrib   = ast.literal_eval(splitted[0])
        self.requestDistrib    = ast.literal_eval(splitted[1])
        self.delayDistrib      = ast.literal_eval(splitted[2])
        self.connectionLength  = ast.literal_eval(splitted[3])
        self.HostPairFrequency = ast.literal_eval(splitted[4])

    def gen_input(self, tuple_list):
        x = []
        y = []

        for theTuple in tuple_list:
            x.append(theTuple[0])
            y.append(theTuple[2])

        return x,y
    
    def gen_graph(self):
        # pgfplot the shits here keku


        plt.figure(1)

        # let x be list of all x values
        # let y be list of all y values
        # linear
        x,y = self.gen_input(self.responseDistrib)
        plt.subplot(221)
        plt.plot(x, y)
        plt.yscale('linear')
        plt.title('Request Size')
        plt.grid(True)


        # log
        x,y = self.gen_input(self.requestDistrib)
        plt.subplot(222)
        plt.plot(x, y)
        plt.yscale('linear')
        plt.title('Response Size')
        plt.grid(True)


        # symmetric log
        x,y = self.gen_input(self.delayDistrib)
        plt.subplot(223)
        plt.plot(x, y)
        plt.yscale('linear')
        plt.title('RTT')
        plt.grid(True)

        # Format the minor tick labels of the y-axis into empty strings with
        # `NullFormatter`, to avoid cumbering the axis with too many labels.
        #plt.gca().yaxis.set_minor_formatter(NullFormatter())
        # Adjust the subplot layout, because the logit one may take more space
        # than usual, due to y-tick labels like "1 - 10^{-3}"
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                            wspace=0.35)

        plt.show()
        #print(str(self.responseDistrib))
        #print(str(self.requestDistrib))
        #print(str(self.delayDistrib))
        #print(str(self.connectionLength))
        #print(str(self.HostPairFrequency))
        

if __name__ == "__main__":
    new_clone = clone()
    new_clone.gen_graph()
    pass

