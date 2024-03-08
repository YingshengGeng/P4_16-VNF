import os
import threading
import time
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from cli import RSVPCLI

class NFVController(object):
    def __init__(self):
        """Initializes the topology and data structures
        """

        if not os.path.exists('topology.json'):
            print('Could not find topology object!!!\n')
            raise Exception

        self.topo = load_topo('topology.json')
        self.controllers = {}
        self.init()

        # sorted by timeouts
        self.current_reservations = {}
        self.fun_type = {}

    def init(self):
        """Connects to switches and resets.
        """
        self.connect_to_switches()
        self.reset_states()

    def reset_states(self):
        """Resets registers, tables, etc.
        """
        [controller.reset_state() for controller in self.controllers.values()]
    
    def connect_to_switches(self):
        """Connects to all the switches in the topology and saves them
         in self.controllers.
        """
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port) 


    def set_ipv4_lpm_table(self):
        """We set all the table defaults to reach all the hosts/networks in the network
        """
        for sw_name, controller in self.controllers.items():
            # for all the hosts connected to this switch add the ipv4_lpm entry
            hosts = self.topo.get_hosts_connected_to(sw_name)
            for host in hosts: 
                controller.table_add("ipv4_lpm", "ipv4_forward", [self.topo.get_host_ip(host) + "/32" ], 
                                     [self.topo.get_host_mac(host), str(self.topo.node_to_node_port_num(sw_name, host))])
                
    def set_mpls_tbl_labels(self):
        """We set all the table defaults to reach all the hosts/networks in the network
        """
        # controller.table_add(table_name, action, [match1, match2], [action_parameter1, action_parameter2])
        # for all switches
        for sw_name, controller in self.controllers.items():
            # for all switches connected to this switch add the 2 mplt_tbl entries
            switchs = self.topo.get_switches_connected_to(sw_name);
            for switch in switchs:
                
                controller.table_add("mpls_act", "mpls_forward", [str(self.topo.node_to_node_port_num(sw_name, switch)), "0"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))])
            
            #MARK now the egress switch all connected host
            hosts = self.topo.get_hosts_connected_to(sw_name)
            for host in hosts: 
                controller.table_add("mpls_act", "mpls_finish", [str(self.topo.node_to_node_port_num(sw_name, host)), "1"], 
                                     [])
                
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.11/32", "10.0.2.21"], ["1", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.12/32", "10.0.2.22"], ["2", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.12/32", "10.0.2.21"], ["1", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.12/32", "10.0.2.22"], ["2", "2", "3"]);

        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.21/32", "10.0.1.11"], ["1", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.21/32", "10.0.1.12"], ["2", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.22/32", "10.0.1.11"], ["1", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.22/32", "10.0.1.12"], ["2", "1", "3"]);


if __name__ == '__main__':
    controller = NFVController()

    controller.set_ipv4_lpm_table()
    controller.set_mpls_tbl_labels()