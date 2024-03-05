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
        # initial link capacity
        self.links_capacity = self.build_links_capacity()

        self.update_lock = threading.Lock()
        self.timeout_thread = threading.Thread(target=self.reservations_timeout_thread, args=(1, ))
        self.timeout_thread.daemon = True
        self.timeout_thread.start()

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

    def build_links_capacity(self):
        """Builds link capacities dictionary

        Returns:
            dict: {edge: bw}
        """

        links_capacity = {}
        return links_capacity
    
    def reservations_timeout_thread(self, refresh_rate = 1):
        """Every refresh_rate checks all the reservations. If any times out
        tries to delete it.

        Args:
            refresh_rate (int, optional): Refresh rate. Defaults to 1.
        """

        while True:
            # sleeps
            time.sleep(refresh_rate)

            # locks the self.current_reservations data structure. This is done
            # because the CLI can also access the reservations.
            with self.update_lock:
                # PART 1, TASK 5.1 Iterate self.current_reservations, update timeout, and if any 
                # entry expired, delete it.
                keys = list(self.current_reservations.keys())
                for key in keys:
                    self.current_reservations[key]["timeout"] -= 1;
                    if self.current_reservations[key]["timeout"] == 0 :
                        self.del_reservation(key[0], key[1])
  

    def set_mpls_tbl_labels(self):
        """We set all the table defaults to reach all the hosts/networks in the network
        """
        # controller.table_add(table_name, action, [match1, match2], [action_parameter1, action_parameter2])
        # for all switches
        for sw_name, controller in self.controllers.items():
            # TODO PART 1 TASK 2
            # 1) for all the hosts connected to this switch add the FEC_tbl entry
            hosts = self.topo.get_hosts_connected_to(sw_name);
            for host in hosts: 
                controller.table_add("FEC_tbl", "ipv4_forward", [ "0.0.0.0/0", self.topo.get_host_ip(host) ], 
                                     [self.topo.get_host_mac(host), str(self.topo.node_to_node_port_num(sw_name, host))]);
    
            # 2) for all switches connected to this switch add the 2 mplt_tbl entries
            switchs = self.topo.get_switches_connected_to(sw_name);
            for switch in switchs:
                controller.table_add("mpls_tbl", "mpls_forward", [str(self.topo.node_to_node_port_num(sw_name, switch)), "0"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))]);
                controller.table_add("mpls_tbl", "penultimate", [str(self.topo.node_to_node_port_num(sw_name, switch)), "1"], 
                                     [self.topo.node_to_node_mac(switch, sw_name), str(self.topo.node_to_node_port_num(sw_name, switch))]);

    def build_mpls_path(self, switches_path):
        """Using a path of switches builds the mpls path. In our simplification
        labels are port indexes. 

        Args:
            switches_path (list): path of switches to allocate

        Returns:
            list: label path
        """
        label_path = []
        # PART 1, TASK 3.2 Get mpls stack of labels
        for i in range(len(switches_path) - 1) :
            current_node = switches_path[i]
            next_node = switches_path[i + 1]
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

    def get_shortest_path(self, src, dst):
        """Computes shortest path. Simple function used to test the system 
        by always allocating the shortest path. 

        Args:
            src (str): src name
            dst (str): dst name

        Returns:
            list: shortest path between src,dst
        """
        
        return self.get_sorted_paths(src, dst)[0]

    def check_if_reservation_fits(self, path, bw):
        """Checks if a the candidate reservation fits in the current
        state of the network. Using the path of switches, checks if all
        the edges (links) have enough space. Otherwise, returns False.

        Args:
            path (list): list of switches
            bw (float): requested bandwidth in mbps

        Returns:
            bool: true if allocation can be performed on path
        """

        # PART 1, TASK 3.1 Implement this function and its helper check_if_reservation_fits
        for link in zip(path, path[1:]):
            if self.links_capacity[link] < bw :
                return False
        return True
    
    def add_link_capacity(self, path, bw):
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
    
    def get_available_path(self, src, dst, bw):
        """Checks all paths from src to dst and picks the 
        shortest path that can allocate bw.

        Args:
            src (str): src name
            dst (str): dst name
            bw (float): requested bandwidth in mbps

        Returns:
            list/bool: best path/ False if none
        """

        # PART 1, TASK 3.1 Implement this function and its helper check_if_reservation_fits
        paths = self.get_sorted_paths(src, dst)
        for path in paths : 
            if self.check_if_reservation_fits(path, bw) :
                return path
        return None


    def get_meter_rates_from_bw(self, bw, burst_size=700000):
        """Returns the CIR and PIR rates and bursts to configure 
          meters at bw.

        Args:
            bw (float): desired bandwdith in mbps
            burst_size (int, optional): Max capacity of the meter buckets. Defaults to 50000.

        Returns:
            list: [(rate1, burst1), (rate2, burst2)]
        """

        # PART 2 TASK 1.2 get the CIR and PIR from bw
        return  [(bw / 8, burst_size), (bw / 8, burst_size)]

    def set_direct_meter_bandwidth(self, sw_name, meter_name, handle, bw):
        """Sets a meter entry (using a table handle) to color packets using
           bw mbps

        Args:
            sw_name (str): switch name
            meter_name (str): meter name
            handle (int): entry handle
            bw (float): desired bandwidth to rate limit
        """

        # PART 2 TASK 1.3 use the controller to configure the meter
        rates = self.get_meter_rates_from_bw(bw)
        # meter_set_rates(meter_name, index, rates)
        self.controllers[sw_name].meter_set_rates(meter_name, handle, rates)

    def add_reservation(self, src, dst, duration, bandwidth, priority):
        """[summary]

        Args:
            src (str): src name
            dst (str): dst name
            duration (float): reservation timeout
            bw (float): requested bandwidth in mbps
            priority (int): reservation priority
        """
       
        # locks the self.current_reservations data structure. This is done
        # because there is a thread that could access it concurrently.
        with self.update_lock:

            # PART 1, TASK 3.4 check if there is an existing reservation for (src,dst). 
            # you can use the self.current_reservations dictionary to check it.
            # If the reservation exists get the path and bw and update the links capacity 
            # data structure using `self.add_link_capacity(path, bw)`
            if (src, dst) in self.current_reservations:
                self.add_link_capacity(self.current_reservations[(src, dst)]["path"], bandwidth)
            # PART 1, TASK 3.1. Once get_available_path is implemented call it to get a path.
            path = self.get_available_path(src, dst, bandwidth)

            # PART 1, TASK 3.2 If there is an available path 
            if path:    
                self.add_or_modify(src, dst, duration, bandwidth, priority, path)
                path_str = "->".join(path)
                print("Successful reservation({}->{}): path: {}".format(src, dst, path_str))
            # PART 1, TASK 3.2 otherwise we print no path available
            else:
                self.readd_reserve(src, dst, duration, bandwidth, priority)
                # PART 1, task 4.3 if we dont find a path but the reservation existed
                # you have to erase it while making sure you update links_capacity accordingly 
                # if (src, dst) in self.current_reservations:
                #     self.sub_link_capacity(self.current_reservations[(src, dst)]["path"], bandwidth)
                #     self.del_reservation(src, dst)
                # print("\033[91mRESERVATION FAILURE: no bandwidth available!\033[0m")

    def add_or_modify(self, src, dst, duration, bandwidth, priority, path):
        label_path = self.build_mpls_path(path)
        # PART 1, TASK 3.3 get:
        # 1) ingress switch name
        sw_id = path[0] # att reverse
        # 2) action name using `mpls_ingress_x_hop` set x as number of labels
        action = "mpls_ingress_{}_hop".format(len(label_path));
        # 3) src and dst ips (your match)
        src_ip = self.topo.get_host_ip(src) + "/32"
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
            handle = self.controllers[sw_id].table_modify(table_name, action, handle, label_path)
        else :
            handle = self.controllers[sw_id].table_add(table_name, action, [src_ip, dst_ip], label_path)

        # PART 2  TASK 1.4 Configure the associated meter properly.
        if handle:
            meter_name = "my_meter"
            self.set_direct_meter_bandwidth(sw_id, meter_name, handle, bandwidth)
            # update controllers data structures: self.current_reservation & self.links_capacity
            self.current_reservations[(src, dst)] = {
                "timeout": (duration), 
                "bw": (bandwidth), 
                "priority": (priority), 
                'handle': handle, 
                'path': path
            }
            self.sub_link_capacity(path, bandwidth)
        

    def readd_reserve(self, src, dst, duration, bandwidth, priority):
        # Part 2 (1), virtually del the low priority reservation
        # 这还在锁的范围内，所以不用管锁
        virtually_delist = []
        print("s1->s2 before: {}".format(self.links_capacity[("s1", "s2")]))
        for key in self.current_reservations.keys() :
            if key == (src, dst) :
                continue;
            if self.current_reservations[key]["priority"] < priority :
                virtually_delist.append(key)
                self.add_link_capacity(self.current_reservations[key]["path"], self.current_reservations[key]["bw"])
        
        # Part 2 (2), check if fit
        path = self.get_available_path(src, dst, bandwidth)
        if path:
            # Part 2 (2).1 add entry or modify
            
            self.add_or_modify(src, dst, duration, bandwidth, priority, path)
            print("s1->s2 later: {}".format(self.links_capacity[("s1", "s2")]))
            path_str = "->".join(path)
            print("Successful reservation({}->{}): path: {}".format(src, dst, path_str))    
            # Part 2 (2).2 re_reserve the virtually deleted reservation
            # sort by the priorition
            virtually_delist.sort(key = lambda id : self.current_reservations[id]["priority"], reverse = True)
           
            for key in virtually_delist:
                # check if ok
                v_src = key[0]
                v_dst = key[1]
                v_bandwidth =  self.current_reservations[key]["bw"]
                v_path = self.get_available_path(v_src, v_dst, v_bandwidth)
                if v_path:  
                    v_duration =  self.current_reservations[key]["timeout"]
                    v_priority =  self.current_reservations[key]["priority"]
                    self.add_or_modify(v_src, v_dst, v_duration, v_bandwidth, v_priority, v_path)
                    v_path_str = "->".join(v_path)
                    print("Successful re_reservation({}->{}): path: {}".format(v_src, v_dst, v_path_str))    
                else :
                    if key in self.current_reservations:
                        self.sub_link_capacity(self.current_reservations[key]["path"], v_bandwidth)
                        self.del_reservation(v_src, v_dst)
                print("Deleting allocation {}->{} due to a higher priority allocation!".format(v_src, v_dst))
        else:   
            if (src, dst) in self.current_reservations:
                self.sub_link_capacity(self.current_reservations[(src, dst)]["path"], bandwidth)
                self.del_reservation(src, dst)
            print("\033[91mRESERVATION FAILURE: no bandwidth available!\033[0m")
            

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