import os, socket, struct
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from cli import VNFCLI
from crc import Crc

crc32_polinomials = [0x04C11DB7, 0xEDB88320, 0xDB710641, 0x82608EDB, 0x741B8CD7, 0xEB31D82E,
                     0xD663B05, 0xBA0DC66B, 0x32583499, 0x992C1A4C, 0x32583499, 0x992C1A4C]

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
            key: label_path (list)
            value: handle (str)
        """
        self.current_mpls_path = {(src, dst):{} for src in self.topo.get_hosts().keys() for dst in self.topo.get_hosts().keys()}
        self.current_path = {(src, dst):[] for src in self.topo.get_hosts().keys() for dst in self.topo.get_hosts().keys()}

        self.firewall_policy = {}
        """
            key: (src, dst) (tuple)
            value: handle (str)
        """
        
        self.registers = {}
        


    def flow_to_bytestream(self, flow):
        return socket.inet_aton(flow[0]) + socket.inet_aton(flow[1])
        # + struct.pack(">HHB",flow[2], flow[3], 6)
    
    def set_crc_custom_hashes(self):
        for controller in self.controllers.values():
            i = 0
            for custom_crc32, width in sorted(self.custom_calcs.items()):
                controller.set_crc32_parameters(custom_crc32, crc32_polinomials[i], 0xffffffff, 0xffffffff, True, True)
                i+=1
    def create_hashes(self):
        self.hashes = []
        for i in range(self.register_num):
            self.hashes.append(Crc(32, crc32_polinomials[i], True, 0xffffffff, True, 0xffffffff))


    def write_policy(self, sw_name, flow, mod):
        controller = self.controllers[sw_name]
        for i in range(self.register_num):
            index = self.hashes[i].bit_by_bit_fast(self.flow_to_bytestream(flow)) % mod
            # register_write(register_name, index, value)
            past_nums = controller.register_read("sketch{}".format(i), index)
            past_nums += 1
            print("i:{}, past_nums:{}".format(i, past_nums))
            controller.register_write("sketch{}".format(i), index, past_nums)
    
    def del_policy(self, sw_name, flow, mod):
        controller = self.controllers[sw_name]
        for i in range(self.register_num):
            index = self.hashes[i].bit_by_bit_fast(self.flow_to_bytestream(flow)) % mod
            # register_write(register_name, index, value)
            past_nums = controller.register_read("sketch{}".format(i), index)
            past_nums -= 1
            print("i:{}, past_nums:{}".format(i, past_nums))
            controller.register_write("sketch{}".format(i), index, past_nums)

    def init(self):
        """Connects to switches and resets.
        """
        self.connect_to_switches()
        self.reset_states()


        self.set_crc_custom_hashes()
        self.create_hashes()

    def reset_states(self):
        """Resets registers, tables, etc.
        """
        [controller.reset_state() for controller in self.controllers.values()]
    
    def connect_to_switches(self):
        """Connects to all the switches in the topology and saves them
         in self.controllers.
        """
        self.custom_calcs = {}
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port) 
            self.custom_calcs[p4switch] = self.controllers[p4switch].get_custom_crc_calcs()
            self.register_num =  len(self.custom_calcs[p4switch])
            

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
                #normal
                controller.table_add("mpls_act", "mpls_finish", [str(0), "1"], 
                                     [])
                #firewall
                controller.table_add("mpls_act", "mpls_forward_and_firewall_active", [str(0 + 100), "1"], 
                                     [])
    
    def set_FEC_tbl_table(self):
        """We set all the mpls FEC defaults to reach all the hosts in the network
        """
        hosts =  self.topo.get_hosts().keys()
        for src_host in hosts:
            for dst_host in hosts:
                #MARK consider the one hop situation
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
        
        # MARK: the last is just a label to idetify function
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

        #record the information in current_mpls_path
        if (src, dst) in self.current_mpls_path:
            self.current_mpls_path[(src, dst)] = {tuple(label_path):handle}
            self.current_path[(src, dst)].append(path)
        

        
        #TEST
        path_str = "->".join(path)
        print("Successful reservation({}->{}): path: {}".format(src, dst, path_str))
    
    def add_mpls_path(self, src, dst):
        """We set the mpls FEC defaults to reach dst from src

        Args:
            src (str): src name
            dst (str): dst name
        """
        self.ecmp_group = {sw_name: {} for sw_name in self.topo.get_p4switches().keys()}
        #MARK this path contains the host
        paths = self.topo.get_shortest_paths_between_nodes(src, dst)
        paths = [x[1:-1] for x in paths] # remove the src and dst host

        # If there is only one available path, directly add
        if paths and len(paths) == 1:    
            path = paths[0]
            self.add_normal_path(src, dst, path)
           
        # If there are more than one available path, add an ecmp group
        elif len(paths) > 1 :
            #use the next hops to identify an group
            ecmp_group_id = 0;
            ingress_sw = paths[0][0] # MARK just one
            next_hops = [x[1] for x in paths]
            next_hops_sw = list(set(next_hops))# remove the duplicates
            print("src: {}, dst: {}, next_hops: {}".format(src, dst, next_hops_sw)) # TEST

            if tuple(next_hops_sw) in self.ecmp_group[ingress_sw].keys():
                ecmp_group_id = self.ecmp_group[ingress_sw][tuple(next_hops_sw)]
            else:           
                ecmp_group_id = len(self.ecmp_group[ingress_sw]) + 1
                self.ecmp_group[ingress_sw][tuple(next_hops_sw)] = ecmp_group_id;

            nhops = len(paths) #MARK
            self.controllers[ingress_sw].table_add("FEC_tbl", "ecmp_group", [self.topo.get_host_ip(src) + "/32", self.topo.get_host_ip(dst)],
                                [str(ecmp_group_id), str(nhops)]);
            #add relevent entry to ecmp_group_to_nhop table
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
                
                #record the information in current_mpls_path
                if (src, dst) in self.current_mpls_path:
                    self.current_mpls_path[(src, dst)][tuple(label_path)] = handle
                    self.current_path[(src, dst)].append(paths[id])
                    


        else:
             print("\033[91mRESERVATION FAILURE: no such path in src: {}, dst: {} available!\033[0m".format(src, dst))

    def add_firewall_policy(self, src, dst):
        """We set the firewall policy base on src_ip, dst_ip

        Args:
            src (str): src name
            dst (str): dst name
        """
        sw_name = self.topo.get_host_gateway_name(src)
        print("gateway: {}".format(sw_name))
        
        #add the rule to the ingress switch
        src_ip = self.topo.get_host_ip(src)
        dst_ip = self.topo.get_host_ip(dst)
        # handle = self.controllers[sw_name].table_add("firewall_tbl", "drop", [src_ip, dst_ip], [])
        self.write_policy(sw_name, (src_ip, dst_ip), 4096) #MARK 可以作为参数
        self.firewall_policy[(src_ip, dst_ip)] = 0
        
        #change the mpls path to start the service
        label_paths_tuple = list(self.current_mpls_path[(src, dst)].keys())
        print(label_paths_tuple)
        #If no ECMP, directly change it  
        if len(label_paths_tuple) == 1:
            table_name = "FEC_tbl";
            label_path_tuple = label_paths_tuple[0]
            self.change_firewall_mpls_path(src, dst, table_name, sw_name, label_path_tuple, 100)
        #If has ECMP, change eache on 
        elif len(label_paths_tuple) > 1:
            table_name = "ecmp_group_to_nhop";
            for label_path_tuple in label_paths_tuple:
                self.change_firewall_mpls_path(src, dst, table_name, sw_name, label_path_tuple, 100)

    def change_firewall_mpls_path(self, src, dst, table_name, sw_name, label_path_tuple, num):
        """We set the firewall policy base on src_ip, dst_ip

        Args:
            src (str): src name
            dst (str): dst name
            table_name (str)
            sw_name (str)
            label_path_tuple (tuple)
        """
        handle = self.current_mpls_path[(src, dst)][label_path_tuple]
        self.current_mpls_path[(src, dst)].pop(label_path_tuple)
        action = "mpls_ingress_{}_hop".format(len(label_path_tuple))
        new_label_path = list(label_path_tuple)
        new_label_path[-1] = (str)((int)(new_label_path[-1]) + num) #MARK the order is reverse
        handle = self.controllers[sw_name].table_modify(table_name, action, handle, new_label_path)
        print(new_label_path)
        self.current_mpls_path[(src, dst)][tuple(new_label_path)] = handle

    def del_firewall_policy(self, src, dst):
        """We delete the firewall policy base on src_ip, dst_ip

        Args:
            src (str): src name
            dst (str): dst name
        """
        sw_name = self.topo.get_host_gateway_name(src)
        print("gateway: {}".format(sw_name))
        src_ip = self.topo.get_host_ip(src)
        dst_ip = self.topo.get_host_ip(dst)
        # handle = self.firewall_policy[(src_ip, dst_ip)]
        # self.controllers[sw_name].table_delete("firewall_tbl", handle, True)
        self.del_policy(sw_name, (src_ip, dst_ip), 4096)

        #change the mpls path to close the service
        label_paths_tuple = list(self.current_mpls_path[(src, dst)].keys())
        print(label_paths_tuple)
        #No ECMP
        if len(label_paths_tuple) == 1:
            table_name = "FEC_tbl";
            label_path_tuple = label_paths_tuple[0]
            self.change_firewall_mpls_path(src, dst, table_name, sw_name, label_path_tuple, -100)

        elif len(label_paths_tuple) > 1:
            table_name = "ecmp_group_to_nhop";
            for label_path_tuple in label_paths_tuple:
                handle = self.current_mpls_path[(src, dst)][label_path_tuple]
                self.change_firewall_mpls_path(src, dst, table_name, sw_name, label_path_tuple, -100)
        self.firewall_policy.pop((src_ip, dst_ip)) 
if __name__ == '__main__':
    controller = NFVController()

    controller.set_ipv4_lpm_table()
    controller.set_mpls_act_table()
    controller.set_FEC_tbl_table()
    controller.add_firewall_policy("h21", "h11")
    controller.del_firewall_policy("h21", "h11")
    cli = VNFCLI(controller)