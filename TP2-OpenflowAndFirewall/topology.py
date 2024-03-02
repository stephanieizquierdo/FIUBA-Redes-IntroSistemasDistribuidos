
from mininet.log import setLogLevel, info

from mininet.topo import Topo

class MyTopo(Topo):
    def __init__(self, switches):
        Topo.__init__(self)

        if switches < 1:
            raise Exception("You need to set at least one switch.")

        switches_list = []
        for switch in range(0, switches):
            switches_list.append(self.addSwitch(f'switch_{switch}'))
            info(f'Added switch switch_{switch}')

        host_1 = self.addHost("host_1")
        self.addLink(switches_list[0], host_1)

        host_2 = self.addHost("host_2")
        self.addLink(switches_list[0], host_2)

        host_3 = self.addHost("host_3")
        self.addLink(switches_list[-1], host_3)

        host_4 = self.addHost("host_4")
        self.addLink(switches_list[-1], host_4)

        for i in range(1, len(switches_list)):
            info(2, 'Added link switches len:' + str(len(switches_list)) + 'i:' + str(i) + 'i - 1:' + str(i - 1))
            self.addLink(switches_list[i - 1], switches_list[i])


topos = {'customTopo': MyTopo}
