from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import utilities as util
import constants

class SingleSwitchTopo(Topo):

    def build(self, servers):
        switch = self.addSwitch('s1')
        for serv in range( 0, len(servers) ):
            host = self.addHost('server%s' % (serv))
            host.setIP(servers[serv])
            self.addLink(host, switch)

        host = self.addHost('client1')
        host.setIP(constants.CLIENT_IP)
        self.addLink(host, switch)

def startup():

    # RUN PRE PROCESS HERE
    
    raw_data = util.get_packet_list()
    client_IP_list, server_IP_list = extract_IPs(raw_data)
    # RAW_DATA OUTPUT
    #         pay     delay time       resp      src_ip            dst_ip   conn_ender
    # ('TCP', 58, 0.003567868470993611, 42, ('10.147.80.139', '10.16.5.225'), 0)
    

    # pass list of IPs
    topo = SingleSwitchTopo(servers=server_IP_list)
    net = Mininet(topo) 
    net.start()
    
    # let each host run their respective stuff

def extract_IPs(raw_data):
    source_list = set([])
    dest_list = set([])
    for x in raw_data:
       the_tuple = x[4]
       source_list.add(the_tuple[0])
       dest_list.add(the_tuple[1])
    return source_list, dest_list

if __name__ == '__main__':
    setLogLevel('info')
    startup()
