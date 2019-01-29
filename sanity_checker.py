#import netifaces as ni
#
#
#ip_not_found = True
#counter = 1
#ip = "NA"
#while ip_not_found:
#    try:
#        interface = "h" + str(counter) + "-eth0"
#        print("mayube")
#        ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
#        ip_not_found = False
#        pass
#    except:
#        counter = counter + 1
#        print(str(counter) + " not the one")
#        ip_not_found = True
#        pass
#print(ip)


#def lodi(): 
#    print("bobo mo potah")
#
#
#if __name__ == "__main__":
#    pass


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import utilities as util
import constants


class SingleSwitchTopo(Topo):

    def build(self):
        switch = self.addSwitch('s1')

        host = self.addHost('h1')
        host.setIP("192.168.145.44")
        self.addLink(host, switch)

        host = self.addHost('h2')
        host.setIP("192.168.145.45")
        self.addLink(host, switch)


def startyo(): 
    topo = SingleSwitchTopo()
    net = Mininet(topo) 
    net.start()

    hosts = net.hosts
    print "Starting test..."
    server = hosts[0]
    popens = {}
    for h in hosts:
        if h.IP() == '192.168.145.44':
            h.cmd("cd " + constants.MODEL_PATH + "; thematrix ndsg-model;")
            popens[h] = h.popen('python3', constants.SERVER_SCRIPT_PATH)
        else:
            pass



    # run client scripts
    # wait for client scripts to finish
    # terminate all values on popens
    # p.values() for p in popens
    # terminate mininet

if __name__ == "__main__":
    startyo()
