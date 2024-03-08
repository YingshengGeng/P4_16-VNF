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
            hosts = self.topo.get_hosts_connected_to(sw_name);
            for host in hosts: 
                controller.table_add("ipv4_lpm", "ipv4_forward", [self.topo.get_host_ip(host) ], 
                                     [self.topo.get_host_mac(host), str(self.topo.node_to_node_port_num(sw_name, host))]);
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
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))]);
                controller.table_add("mpls_tbl", "penultimate", [str(self.topo.node_to_node_port_num(sw_name, switch)), "1"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))]);



    def build_mpls_path(self, switches_path, sw_node, service_type):
        
        """Using a path of switches builds the mpls path. In our simplification
        labels are port indexes. 

        Args:
            switches_path (list): path of switches to allocate

        Returns:
            list: label path
        """
        #TODO label and service
        label_path = []
        # PART 1, TASK 3.2 Get mpls stack of labels
        for i in range(len(switches_path) - 1) :
            current_node = switches_path[i]
            next_node = switches_path[i + 1]
            if current_node == sw_node :
                label_path.append(self.service_to_label(service_type));
            else :
                label_path.append(self.topo.node_to_node_port_num(current_node, next_node))
        
        # Att: the last is not need;
        # label_path.reverse();
        return label_path[::-1]

    def get_sorted_paths(self, src, dst):
        """Gets all paths between src, dst 
        sorted by length. This function uses the internal networkx API.

        Args:
            src (str): src name
            dst (str): dst name

        Returns:
            list: paths between src and dst
        """

        paths = self.topo.get_all_paths_between_nodes(src, dst)
        # trim src and dst
        paths = [x[1:-1] for x in paths]
        return paths



    def check_if_reservation_fits(self, path, sw_node):
        #TODO check if match
        """Checks if a the candidate reservation fits in the current
        state of the network. Using the path of switches, checks if the paths
        have the sw_node. Otherwise, returns False.

        Args:
            path (list): list of switches
            sw_node (str): requested service node

        Returns:
            bool: true if allocation can be performed on path
        """
        if sw_node not in path:
            return False;
        return True

    def get_available_path(self, src, dst, sw_node, service_type):
        """Checks all paths from src to dst and picks the 
        shortest path that can allocate bw.

        Args:
            src     (str): src name
            dst     (str): dst name
            sw_node (str): requested service node
            service_type (str): requested service type

        Returns:
            list/bool: best path/ False if none
        """

        # PART 1, TASK 3.1 Implement this function and its helper check_if_reservation_fits
        paths = self.get_sorted_paths(src, dst)
        for path in paths : 
            if self.check_if_reservation_fits(path, sw_node, service_type) :
                return path
        return False
    
    def add_link_capacity(self, path, bw):
        # TODO change ther service
        """Adds bw capacity to a all the edges along path. This 
        function is used when an allocation is removed.

        Args:
            path (list): list of switches
            bw (float): requested bandwidth in mbps
        """

         # PART 1, TASK 3.4 add bw to edges
        for link in zip(path, path[1:]):
            self.links_capacity[link] += bw

    def sub_link_capacity(self, path, bw):
        """subtracts bw capacity to a all the edges along path. This 
        function is used when an allocation is added.

        Args:
            path (list): list of switches
            bw (float): requested bandwidth in mbps
        """
        
        # PART 1, TASK 3.4 sub bw to edges
        for link in zip(path, path[1:]):
            self.links_capacity[link] -= bw

    def add_reservation(self, src, dst, duration, sw_node, service_type, priority):
        """Add a reservation between src and dst, if resources meet demands.

        Args:
            src (str): src name
            dst (str): dst name
            duration (float): reservation timeout
            sw_node (str): requested service node
            service_type (str): requested service type
            priority (int): reservation priority
        """
        # TODO if if there is an existing reservation for (src, dst).
        if (src, dst) in self.current_reservations[sw_node][service_type]:
            pass    
        
        path = self.get_available_path(src, dst, sw_node, service_type)
        # print("request node: {}, return path: {}".format(sw_node, path))
        if path:
            self.add_or_modify(src, dst, duration, sw_node, service_type, priority, path)
            path_str = "->".join(path)
            print("Successful add service({}->{}): path: {}".format(service_type, sw_node, path_str))
        else:
            print("\033[91mRESERVATION FAILURE: no path for this service available!\033[0m")

    def service_to_label (service_type) :
        match service_type:
            case "Firewall" :
                return 1 << 4;
            case "Load_Balance" :
                return 1 << 5;

    def add_or_modify(self, src, dst, duration, sw_node, service_type, priority, path):
        label_path = self.build_mpls_path(path, sw_node, service_type)

        # 1) ingress switch name
        ingress_id = path[0] # att reverse
        # 2) action name using `mpls_ingress_x_hop` set x as number of labels
        action = "mpls_ingress_{}_hop".format(len(label_path));
        # 3) src and dst ips (your match)
        src_ip = self.topo.get_host_ip(src) + "/32" #TODO
        dst_ip = self.topo.get_host_ip(dst)
        # 4) make sure all your labels are strings and use them as action parameters
        label_path = [str(label) for label in label_path]
        table_name = "FEC_tbl";
        # other para
        handle = 0;
        # PART 1, TASK 3.4
        # check if its a new or an existing reservation (to update)
        # add entry or modify
        if (src, dst) in self.current_reservations :
            #这里还没有test
            handle = self.current_reservations[(src, dst)]["handle"]
            handle = self.controllers[ingress_id].table_modify(table_name, action, handle, label_path)
        else :
            handle = self.controllers[ingress_id].table_add(table_name, action, [src_ip, dst_ip], label_path)

            # PART 2  TASK 1.4 Configure the associated meter properly.
        if handle:
            meter_name = "my_meter"
            self.set_direct_meter_bandwidth(ingress_id, meter_name, handle, bandwidth)
            # update controllers data structures: self.current_reservation & self.links_capacity
            self.current_reservations[(src, dst)] = {
                "timeout": (duration), 
                "bw": (bandwidth), 
                "priority": (priority), 
                'handle': handle, 
                'path': path
            }
            self.sub_link_capacity(path, bandwidth)
        
    def add_firewall_entry(self, ):
    def del_reservation(self, src, dst):
        """Deletes a reservation between src and dst, if exists. To 
        delete the reservation the self.current_reservations data structure 
        is used to retrieve all the needed information. After deleting the reservation
        from the ingress switch, path capacities are updated.

        Args:
            src (str): src name
            dst (str): dst name
        """

        # PART 1, TASK 4.1 remove the reservation from the switch, controller and update links capacities.
        if (src, dst) in self.current_reservations :
            reserve_info = self.current_reservations[(src, dst)];
            # switch
            sw_id = reserve_info["path"][0];
            path_str =  "->".join(reserve_info["path"])
            self.controllers[sw_id].table_delete("FEC_tbl", reserve_info["handle"], True)
            # link
            self.add_link_capacity(reserve_info["path"], reserve_info["bw"])
            #controller
            self.current_reservations.pop((src, dst));
            print("RSVP Deleted/Expired Reservation({}->{}): path: {}".format(src, dst, path_str))
    def del_all_reservations(self):
        """Deletes all the current reservations
        """

        # locks the self.current_reservations data structure. This is done
        # because there is a thread that could access it concurrently.
        with self.update_lock:
            # PART 1, TASK 4.2 remove all the reservations      
            for key in self.current_reservations.keys():
                self.del_reservation(key[0], key[1]);  #是否能优化


if __name__ == '__main__':
    controller = RSVPController()
    controller.set_mpls_tbl_labels()
    cli = RSVPCLI(controller)




    #ipv4_forward
#externel
table_add  ipv4_lpm ipv4_forward 10.0.1.11/32 =>  00:00:0a:00:01:0b 1
table_add  ipv4_lpm ipv4_forward 10.0.1.12/32 =>  00:00:0a:00:01:0c 2

#mpls_header
table_add  FEC_tbl mpls_ingress_3_hop 10.0.1.0/24 10.0.2.21 =>  1 2 6
table_add  FEC_tbl mpls_ingress_3_hop 10.0.1.0/24 10.0.2.22 =>  2 2 3

#mpls forward 
table_add  mpls_tbl mpls_forward 3 0 => 86:92:45:17:ac:f4 3
table_add  mpls_tbl mpls_forward 4 0 => 52:46:50:00:d9:b8 4
table_add  mpls_tbl penultimate 1 1 => 00:00:0a:00:01:0b 1
table_add  mpls_tbl penultimate 2 1 => 00:00:0a:00:01:0c 2

#mpls_function
#table_add  mpls_nfc bloom_filter 3 => 
#table_add  mpls_nfc bloom_filter 4 => 
#table_add  mpls_nfc bloom_filter 1 => 
#table_add  mpls_nfc bloom_filter 2 => 

#firewall
table_add  check_ports set_direction 3 1 => 1
table_add  check_ports set_direction 4 1 => 1
table_add  check_ports set_direction 3 2 => 1
table_add  check_ports set_direction 4 2 => 1

#load_balance
table_add  mpls_nfc ecmp_group 6 => 1 2
table_add  ecmp_group_to_forward mpls_forward 1 0 => 86:92:45:17:ac:f4 3
table_add  ecmp_group_to_forward mpls_forward 1 1 => 52:46:50:00:d9:b8 4




#ipv4_forward
table_add  ipv4_lpm ipv4_forward 10.0.2.21/32 => 00:00:0a:00:02:15 1
table_add  ipv4_lpm ipv4_forward 10.0.2.22/32 => 00:00:0a:00:02:16 2

#mpls_header
table_add  FEC_tbl mpls_ingress_3_hop 10.0.2.0/24 10.0.1.11 =>  1 1 6
table_add  FEC_tbl mpls_ingress_3_hop 10.0.2.0/24 10.0.1.12 =>  2 1 3

#mpls forward
table_add  mpls_tbl mpls_forward 3 0 => ca:a1:30:43:1d:5e 3
table_add  mpls_tbl mpls_forward 4 0 => 2e:f8:9c:32:03:9c 4
table_add  mpls_tbl penultimate 1 1 => 00:00:0a:00:02:15 1
table_add  mpls_tbl penultimate 2 1 => 00:00:0a:00:02:16 2
#mpls_function
#fire_wall

#load_balance
table_add  mpls_nfc ecmp_group 6 => 1 2
table_add  ecmp_group_to_forward mpls_forward 1 0 => ca:a1:30:43:1d:5e 3
table_add  ecmp_group_to_forward mpls_forward 1 1 => 2e:f8:9c:32:03:9c 4