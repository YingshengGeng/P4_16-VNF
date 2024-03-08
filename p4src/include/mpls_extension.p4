// action mpls_ingress_1_hop(label_t label_1) {

//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;
// }

// action mpls_ingress_2_hop(label_t label_1, label_t label_2) {
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_3_hop(label_t label_1, label_t label_2, label_t label_3) {
    
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_4_hop(label_t label_1, label_t label_2, label_t label_3, label_t label_4) {
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_4;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_5_hop(label_t label_1, label_t label_2, label_t label_3, label_t label_4, label_t label_5) {
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_4;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_5;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_6_hop(label_t label_1, label_t label_2, label_t label_3, label_t label_4, label_t label_5, label_t label_6) {
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_4;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_5;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_6;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_7_hop(label_t label_1, label_t label_2, label_t label_3, label_t label_4, label_t label_5, label_t label_6, label_t label_7) {
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_4;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_5;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_6;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_7;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }

// action mpls_ingress_8_hop(label_t label_1, label_t label_2, label_t label_3, label_t label_4, label_t label_5, label_t label_6, label_t label_7, label_t label_8) {
    
//     hdr.ethernet.etherType = TYPE_MPLS;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_1;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 1;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_2;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_3;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_4;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_5;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_6;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_7;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;

//     hdr.mpls.push_front(1);
//     hdr.mpls[0].setValid();
//     hdr.mpls[0].label = label_8;
//     hdr.mpls[0].ttl = hdr.ipv4.ttl - 1;
//     hdr.mpls[0].s = 0;
// }





//     action drop() {
//         mark_to_drop(standard_metadata);
//     }

//     action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {

//         hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
//         hdr.ethernet.dstAddr = dstAddr;

//         standard_metadata.egress_spec = port;
//         hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
//     }

//     action mpls_forward(macAddr_t dstAddr, egressSpec_t port) {

//         hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
//         hdr.ethernet.dstAddr = dstAddr;

//         standard_metadata.egress_spec = port;

//         hdr.mpls[1].ttl = hdr.mpls[0].ttl - 1;

//         hdr.mpls.pop_front(1);
//     }

//     action penultimate(macAddr_t dstAddr, egressSpec_t port) {

//         hdr.ethernet.etherType = TYPE_IPV4;

//         hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
//         hdr.ethernet.dstAddr = dstAddr;

//         hdr.ipv4.ttl = hdr.mpls[0].ttl - 1;

//         standard_metadata.egress_spec = port;
//         hdr.mpls.pop_front(1);
//     }

//     action ecmp_group(bit<14> ecmp_group_id, bit<16> num_nhops) {

//         meta.ecmp_group_id = ecmp_group_id;
//         //hash(output_field, (crc16 or crc32), (bit<1>)0, {fields to hash}, (bit<16>)modulo)
//         //five tuple: src ip, dst ip, src port, dst port, protocol
//         hash(meta.ecmp_hash, HashAlgorithm.crc32, (bit<1>)0, 
//             {hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, hdr.tcp.srcPort,hdr.tcp.dstPort, hdr.ipv4.protocol}, 
//             num_nhops);
        
//     }

//     action compute_hashes(ip4Addr_t ipAddr1, ip4Addr_t ipAddr2, bit<16> port1, bit<16> port2) {
//        //Get register position
//        hash(reg_pos_one, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1,
//                                                            ipAddr2,
//                                                            port1,
//                                                            port2,
//                                                            hdr.ipv4.protocol},
//                                                            (bit<32>)BLOOM_FILTER_ENTRIES);

//        hash(reg_pos_two, HashAlgorithm.crc32, (bit<32>)0, {ipAddr1,
//                                                            ipAddr2,
//                                                            port1,
//                                                            port2,
//                                                            hdr.ipv4.protocol},
//                                                            (bit<32>)BLOOM_FILTER_ENTRIES);
//     }

//     action set_direction(bit<1> dir) {
//         direction = dir;
//     }

//     action bloom_filter(bit<1> direction) {
//         if (direction == 0) {
//             compute_hashes(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, hdr.tcp.srcPort, hdr.tcp.dstPort);
//         } else {
//             compute_hashes(hdr.ipv4.dstAddr, hdr.ipv4.srcAddr, hdr.tcp.dstPort, hdr.tcp.srcPort);
//         }
//         // Packet comes from internal network
//         if (direction == 0) {
//             // If there is a syn we update the bloom filter and add the entry
//             if (hdr.tcp.syn == 1){
//                 bloom_filter_1.write(reg_pos_one, 1);
//                 bloom_filter_2.write(reg_pos_two, 1);
//             }
//         // Packet comes from outside
//         } else if (direction == 1) {
//             // Read bloom filter cells to check if there are 1's
//             bloom_filter_1.read(reg_val_one, reg_pos_one);
//             bloom_filter_2.read(reg_val_two, reg_pos_two);
//             // only allow flow to pass if both entries are set
//             if (reg_val_one != 1 || reg_val_two != 1) {
//                 drop();
//             }
//         }
//     }