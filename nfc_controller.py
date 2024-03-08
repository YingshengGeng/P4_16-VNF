import os
import threading
import time
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from cli import VNFCLI

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

        self.ecmp_group = {}
        """
            key: switch_name (str)
            value: { path: ecmp_id } (dict)
        """
        self.ecmp_group = {sw_name: {} for sw_name in self.topo.get_p4switches().keys()}
        
        self.current_mpls_path = {}
        """
            key: label_path (list
            value: handle (str)
        """
        self.current_mpls_path = {(src, dst):{} for src in self.topo.get_hosts().keys() for dst in self.topo.get_hosts().keys()}
        
        self.fire_wall_policy = {}
        """
            key: (src, dst) (tuple)
            value: handle (str)
        """
        

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
        """We set all the ipv4 table defaults to reach all the host in the network
        """
        for sw_name, controller in self.controllers.items():
            # for all the hosts connected to this switch add the ipv4_lpm entry
            hosts = self.topo.get_hosts_connected_to(sw_name)
            for host in hosts: 
                controller.table_add("ipv4_lpm", "ipv4_forward", [self.topo.get_host_ip(host) + "/32" ], 
                                     [self.topo.get_host_mac(host), str(self.topo.node_to_node_port_num(sw_name, host))])
                
    def set_mpls_act_table(self):
        """We set all the mpls table defaults to reach all the hosts in the network
        """
        # controller.table_add(table_name, action, [match1, match2], [action_parameter1, action_parameter2])
        # for all switches
        for sw_name, controller in self.controllers.items():
            # for all switches connected to this switch add the 2 mplt_tbl entries
            switchs = self.topo.get_switches_connected_to(sw_name);
            for switch in switchs:
                #normal
                controller.table_add("mpls_act", "mpls_forward", [str(self.topo.node_to_node_port_num(sw_name, switch)), "0"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))])
                #firewall
                controller.table_add("mpls_act", "mpls_forward_and_firewall_active", [str(self.topo.node_to_node_port_num(sw_name, switch) + 100), "0"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))])
            #MARK now the egress switch all connected host
            hosts = self.topo.get_hosts_connected_to(sw_name)
            print(hosts)
            for host in hosts: 
                controller.table_add("mpls_act", "mpls_finish", [str(0), "1"], 
                                     [])
                #firewall
                controller.table_add("mpls_act", "mpls_forward_and_firewall_active", [str(0 + 100), "1"], 
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
        handle = self.controllers[ingress_id].table_add(table_name, action, [src_ip_lpm, dst_ip], label_path)

        #save MARK the path now is static
        if (src, dst) in self.current_mpls_path:
            self.current_mpls_path[(src, dst)] = {tuple(label_path):handle}
        else:
            self.current_mpls_path[(src, dst)]  = {}
            self.current_mpls_path[(src, dst)][tuple(label_path)] = handle
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
                
                handle = self.controllers[ingress_sw].table_add(table_name, action, [str(ecmp_group_id), str(id)], 
                                    label_path);
                #save MARK the path now is static
                if (src, dst) in self.current_mpls_path:
                    self.current_mpls_path[(src, dst)][tuple(label_path)] = handle
                else:
                    self.current_mpls_path[(src, dst)] = {}
                    self.current_mpls_path[(src, dst)][tuple(label_path)] = handle
                # nhops - id - 1


        else:
             print("\033[91mRESERVATION FAILURE: no such path in src: {}, dst: {} available!\033[0m".format(src, dst))

    def add_firewall_policy(self, src, dst):
        
        sw_name = self.topo.get_host_gateway_name(src)
        print("gateway: {}".format(sw_name))
        #add the rule
        src_ip = self.topo.get_host_ip(src)
        dst_ip = self.topo.get_host_ip(dst)
        handle = self.controllers[sw_name].table_add("firewall_tbl", "drop", [src_ip, dst_ip], [])
        self.fire_wall_policy[(src_ip, dst_ip)] = handle
        #change the path
        label_paths_tuple = list(self.current_mpls_path[(src, dst)].keys())
        print(label_paths_tuple)
        #No ECMP
        if len(label_paths_tuple) == 1:
            table_name = "FEC_tbl";
            label_path_tuple = label_paths_tuple[0]
            handle = self.current_mpls_path[(src, dst)][label_path_tuple]
            self.current_mpls_path[(src, dst)].pop(label_path_tuple)
            action = "mpls_ingress_{}_hop".format(len(label_path_tuple))
            #udpdate
            new_label_path = list(label_path_tuple)
            new_label_path[-1] = (str)((int)(new_label_path[-1]) + 100) #MARK the reverse
            handle = self.controllers[sw_name].table_modify(table_name, action, handle, new_label_path)
            print(new_label_path)
            self.current_mpls_path[(src, dst)][tuple(new_label_path)] = handle
       
        elif len(label_paths_tuple) > 1:
            table_name = "ecmp_group_to_nhop";
            for label_path_tuple in label_paths_tuple:
                handle = self.current_mpls_path[(src, dst)][label_path_tuple]
                self.current_mpls_path[(src, dst)].pop(label_path_tuple)
                action = "mpls_ingress_{}_hop".format(len(label_path_tuple))
                #udpdate
                new_label_path = list(label_path_tuple)
                new_label_path[-1] = (str)((int)(new_label_path[-1]) + 100) #MARK the reverse
                handle = self.controllers[sw_name].table_modify(table_name, action, handle, new_label_path)
                self.current_mpls_path[(src, dst)][tuple(new_label_path)] = handle
    def del_firewall_policy(self, src, dst):
        
        sw_name = self.topo.get_host_gateway_name(src)
        print("gateway: {}".format(sw_name))
        #add the rule
        src_ip = self.topo.get_host_ip(src)
        dst_ip = self.topo.get_host_ip(dst)
        handle = self.fire_wall_policy[(src_ip, dst_ip)]
        #MARK 加一个handle的存储，其实第一个删除也就是都删除了
        self.controllers[sw_name].table_delete("firewall_tbl", handle, True)

        #change the path
        label_paths_tuple = list(self.current_mpls_path[(src, dst)].keys())
        print(label_paths_tuple)
        #No ECMP
        if len(label_paths_tuple) == 1:
            table_name = "FEC_tbl";
            label_path_tuple = label_paths_tuple[0]
            handle = self.current_mpls_path[(src, dst)][label_path_tuple]
            self.current_mpls_path[(src, dst)].pop(label_path_tuple)
            action = "mpls_ingress_{}_hop".format(len(label_path_tuple))
            #udpdate
            new_label_path = list(label_path_tuple)
            new_label_path[-1] = (str)((int)(new_label_path[-1]) - 100) #MARK decrease
            handle = self.controllers[sw_name].table_modify(table_name, action, handle, new_label_path)
            print(new_label_path)
            self.current_mpls_path[(src, dst)][tuple(new_label_path)] = handle
       
        elif len(label_paths_tuple) > 1:
            table_name = "ecmp_group_to_nhop";
            for label_path_tuple in label_paths_tuple:
                handle = self.current_mpls_path[(src, dst)][label_path_tuple]
                self.current_mpls_path[(src, dst)].pop(label_path_tuple)
                action = "mpls_ingress_{}_hop".format(len(label_path_tuple))
                #udpdate
                new_label_path = list(label_path_tuple)
                new_label_path[-1] = (str)((int)(new_label_path[-1]) - 100) #MARK the reverse
                handle = self.controllers[sw_name].table_modify(table_name, action, handle, new_label_path)
                self.current_mpls_path[(src, dst)][tuple(new_label_path)] = handle

if __name__ == '__main__':
    controller = NFVController()

    controller.set_ipv4_lpm_table()
    controller.set_mpls_act_table()
    controller.set_FEC_tbl_table()
    controller.add_firewall_policy("h21", "h11")
    # controller.del_firewall_policy("h21", "h11")
    cli = VNFCLI(controller)