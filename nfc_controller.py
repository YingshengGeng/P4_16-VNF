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
        self.ecmp_group = {}

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
                
    def set_mpls_act_table(self):
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
            print(hosts)
            for host in hosts: 
                controller.table_add("mpls_act", "mpls_finish", [str(0), "1"], 
                                     [])
    
    def set_FEC_tbl_table(self):
        hosts =  self.topo.get_hosts().keys()
        for src_host in hosts:
            for dst_host in hosts:
                #MARK consider the only one router
                if src_host == dst_host:
                    continue
                else:
                    self.add_mpls_path(src_host, dst_host);


    def build_mpls_path(self, switches_path):
        """Using a path of switches builds the mpls path. In our simplification
        labels are port indexes. 

        Args:
            switches_path (list): path of switches to allocate

        Returns:
            list: label path
        """
        label_path = []
        for i in range(len(switches_path) - 1) :
            current_node = switches_path[i]
            next_node = switches_path[i + 1]
            label_path.append(self.topo.node_to_node_port_num(current_node, next_node))
        
        # MARK: the last is just a label
        label_path.append(0)
        return label_path[::-1]

    def add_normal_path(self, src, dst, path):

        # 1) ingress switch name
        ingress_id = path[0]
        label_path = self.build_mpls_path(path)
        # 2) action name using `mpls_ingress_x_hop` set x as number of labels
        action = "mpls_ingress_{}_hop".format(len(label_path)); action = "mpls_ingress_{}_hop".format(len(label_path));
        # 3) src and dst ips (your match)
        src_ip_lpm = self.topo.get_host_ip(src) + "/32"
        dst_ip = self.topo.get_host_ip(dst)
        # 4) make sure all your labels are strings and use them as action parameters
        label_path = [str(label) for label in label_path]
        table_name = "FEC_tbl";
        self.controllers[ingress_id].table_add(table_name, action, [src_ip_lpm, dst_ip], label_path)

        #TEST
        path_str = "->".join(path)
        print("Successful reservation({}->{}): path: {}".format(src, dst, path_str))
        
    def add_mpls_path(self, src, dst):
        """[summary]

        Args:
            src (str): src name
            dst (str): dst name
        """
        self.ecmp_group = {sw_name: {} for sw_name in self.topo.get_p4switches().keys()}
        #MARK this path contains the host
        paths = self.topo.get_shortest_paths_between_nodes(src, dst)
        paths = [x[1:-1] for x in paths] # remove the src and dst host

        # If there is an available pa
        if paths and len(paths) == 1:    
            path = paths[0]
            self.add_normal_path(src, dst, path)
        
        elif len(paths) > 1 :
            #Get the ECMP group
            ingress_sw = paths[0][0] # MARK just one
            next_hops = [x[1] for x in paths]
            next_hops_sw = list(set(next_hops))# remove the duplicates
            print("src: {}, dst: {}, next_hops: {}".format(src, dst, next_hops_sw)) # TEST

            ecmp_group_id = 0;
            if tuple(next_hops_sw) in self.ecmp_group[ingress_sw].keys():
                ecmp_group_id = self.ecmp_group[ingress_sw][tuple(next_hops_sw)]
            else:           
                ecmp_group_id = len(self.ecmp_group[ingress_sw]) + 1
                self.ecmp_group[ingress_sw][tuple(next_hops_sw)] = ecmp_group_id;

            nhops = len(paths) #MARK

            self.controllers[ingress_sw].table_add("FEC_tbl", "ecmp_group", [self.topo.get_host_ip(src) + "/32", self.topo.get_host_ip(dst)],
                                [str(ecmp_group_id), str(nhops)]);
            for id in range(nhops):
                # 1) ingress switch name
                label_path = self.build_mpls_path(paths[id])
                # 2) action name using `mpls_ingress_x_hop` set x as number of labels
                action = "mpls_ingress_{}_hop".format(len(label_path))
                # 4) make sure all your labels are strings and use them as action parameters
                label_path = [str(label) for label in label_path]
                table_name = "ecmp_group_to_nhop";
                
                self.controllers[ingress_sw].table_add(table_name, action, [str(ecmp_group_id), str(id)], 
                                    label_path);
                # nhops - id - 1


        else:
             print("\033[91mRESERVATION FAILURE: no such path in src: {}, dst: {} available!\033[0m".format(src, dst))


if __name__ == '__main__':
    controller = NFVController()

    controller.set_ipv4_lpm_table()
    controller.set_mpls_act_table()
    controller.set_FEC_tbl_table()
    cli = RSVPCLI(controller)