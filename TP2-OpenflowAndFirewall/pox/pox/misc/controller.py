import os
import json

from pox.core import core
import pox.lib.packet as packet
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.revent.revent import EventMixin
import pox.openflow.libopenflow_01 as openflow

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ['HOME']

class Controller(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        abs_path = os.getcwd()
        config = self.read_config(str(abs_path) + "/rules.json")
        self.firewall_switch_id = config["firewall_switch_id"]
        self.rules = config["rules"]
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp(self, event):
        log.debug("Connection Up Event on router %s", event.dpid)
        if event.dpid == self.firewall_switch_id:
            [self.add_rule(event, rule) for rule in self.rules]
            log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

    def add_rule(self, event, rule):
        match = openflow.ofp_match()
        log.debug("Adding firewall rule")

        if "ip_ver" in rule:
            log.debug("Added ip version to rule: dl_type:%s", rule["ip_ver"])
            if 'ipv4' == rule["ip_ver"]:
                match.dl_type = packet.ethernet.IP_TYPE
            if 'ipv6' == rule["ip_ver"]:
                match.dl_type = packet.ethernet.IPV6_TYPE
        if "dl_src" in rule:
            log.debug("Added dl_src to rule: dl_src:%s", rule["dl_src"])
            match.dl_src = EthAddr(rule["dl_src"])
        if "dl_dst" in rule:
            log.debug("Added dl_dst to rule: dl_dst:%s", rule["dl_dst"])
            match.dl_dst = EthAddr(rule["dl_dst"])
        if "protocol" in rule:
            log.debug("Added protocol to rule: nw_proto:%s", rule["protocol"])
            if rule['protocol'] == "udp":
                match.nw_proto = packet.ipv4.UDP_PROTOCOL
            if rule['protocol'] == 'tcp':
                match.nw_proto = packet.ipv4.TCP_PROTOCOL
        if "src_ip" in rule:
            log.debug("Added src_ip to rule: nw_src:%s", rule["src_ip"])
            match.nw_src = IPAddr(rule["src_ip"])
        if "dst_ip" in rule:
            log.debug("Added dst_ip to rule: nw_dst:%s", rule["dst_ip"])
            match.nw_dst = IPAddr(rule["dst_ip"])
        if "src_port" in rule:
            log.debug("Added src_port to rule: tp_src:%s", rule["src_port"])
            match.tp_src = rule["src_port"]
        if "dst_port" in rule:
            log.debug("Added dst_port to rule: tp_dst:%s", rule["dst_port"])
            match.tp_dst = rule["dst_port"]

        msg = openflow.ofp_flow_mod()
        msg.match = match
        event.connection.send(msg)

    def read_config(self, file):
        file = open(file, "r")
        config = json.loads(file.read())
        file.close()
        return config


def launch():
    core.registerNew(Controller)
