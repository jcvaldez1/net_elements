
from mininet.topo import Topo

class MyTopo( Topo ):
    # "Simple topology example."

    def __init__( self ):
        # "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        switch = self.addSwitch('s1')
        popens = {}
        host = self.addHost('h1')
        self.addLink(host, switch)

        #Host('h1').setIP("192.168.145.44")

        host = self.addHost('h2')
        #host.setIP("192.168.145.45")
        self.addLink(host, switch)
		#popens[host] = host.popen('python3', '~/physical2/working_model/test_client.py')

topos = { 'mytopo': ( lambda: MyTopo() ) }

