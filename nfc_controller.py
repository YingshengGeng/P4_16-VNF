import os
import threading
import time
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from cli import RSVPCLI

class RSVPController(object):
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
                controller.table_add("mpls_tbl", "mpls_forward", [str(self.topo.node_to_node_port_num(sw_name, switch)), "0"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))])
                controller.table_add("mpls_tbl", "penultimate", [str(self.topo.node_to_node_port_num(sw_name, switch)), "1"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))])
            
            hosts = self.topo.get_hosts_connected_to(sw_name)
            for host in hosts: 
                controller.table_add("mpls_tbl", "penultimate", [str(self.topo.node_to_node_port_num(sw_name, host)), "1"], 
                                     [self.topo.get_host_mac(host), str(self.topo.node_to_node_port_num(sw_name, host))])
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.11", "10.0.2.21"], ["1", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.11", "10.0.2.22"], ["2", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.12", "10.0.2.21"], ["1", "2", "3"]);
        self.controllers["s1"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.1.12", "10.0.2.22"], ["2", "2", "3"]);

        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.21", "10.0.1.11"], ["1", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.21", "10.0.1.12"], ["2", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.22", "10.0.1.11"], ["1", "1", "3"]);
        self.controllers["s2"].table_add("FEC_tbl", "mpls_ingress_3_hop", ["10.0.2.22", "10.0.1.12"], ["2", "1", "3"]);

    def service_to_label(self, service_type) :
        match service_type:
            case "Firewall" :
                return 1 << 4
            case "Load_Balance" :
                return 1 << 5
    def add_fw_entry(self, src, dst, sw_id):
        #label match entry
        table_name = "mpls_nfc"
        action = "bloom_filter"
        label = str(self.service_to_label("Firewall"))
        # _ = self.controllers[sw_id].table_add(table_name, action, [label], []);
        for id in range(4):
            _ = self.controllers[sw_id].table_add(table_name, action, [str(id)], []);
        #actual action
        table_name = "check_ports"
        action = "set_direction"
        src_ip =  self.topo.get_host_ip(src)
        dst_ip = self.topo.get_host_ip(dst)
        _ = self.controllers[sw_id].table_add(table_name, action, [src_ip, dst_ip], ["0"]);
        _ = self.controllers[sw_id].table_add(table_name, action, [dst_ip, src_ip], ["1"]);
    
    def add_lb_entry(self, src, dst, sw_id):
        #label match entry
        table_name = "mpls_nfc"
        action = "ecmp_group"
        label = str(self.service_to_label("Load_Balance"))
        ecmp_group_id = "1" #TODO
        num_nhops = "2"
        _ = self.controllers[sw_id].table_add(table_name, action, [label], [ecmp_group_id, num_nhops]);

        table_name = "ecmp_group_to_forward"
        action = "mpls_forward"
        ecmp_group_id = "1"
        ecmp_port = [3, 4]
        for id in range(int(num_nhops)):
            target_node = self.port_to_node(sw_id, ecmp_port[id]);
            target_mac = self.node_to_node_mac(target_node, sw_id);
            target_port = str(ecmp_port[id]);
            self.controllers[sw_id].table_add(table_name, action, [ecmp_group_id, str(id)], [target_mac, target_port]);


if __name__ == '__main__':
    controller = RSVPController()

    controller.set_ipv4_lpm_table()
    controller.set_mpls_tbl_labels()
    cli = RSVPCLI(controller)