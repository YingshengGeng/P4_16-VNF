#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/checksum.p4"
#include "include/parsers.p4"
#include "include/mpls_extension.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {  

    
    register <bit<ID_WIDTH>>(REGISTER_SIZE) flowlet_to_id;
    //MARK: the mpls labels is are reverse
    action mpls_ingress_1_hop(label_t label1) {

        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};
    }

    action mpls_ingress_2_hop(label_t label1, label_t label2) {
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_ingress_3_hop(label_t label1, label_t label2, label_t label3) {
    
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

    }

    action mpls_ingress_4_hop(label_t label1, label_t label2, label_t label3, label_t label4) {
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label4, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_ingress_5_hop(label_t label1, label_t label2, label_t label3, label_t label4, label_t label5) {
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label4, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label5, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_ingress_6_hop(label_t label1, label_t label2, label_t label3, label_t label4, label_t label5, label_t label6) {
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label4, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label5, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label6, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_ingress_7_hop(label_t label1, label_t label2, label_t label3, label_t label4, label_t label5, label_t label6, label_t label7) {
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label4, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label5, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label6, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label7, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_ingress_8_hop(label_t label1, label_t label2, label_t label3, label_t label4, label_t label5, label_t label6, label_t label7, label_t label8) {
    
        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0 ,1, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label2, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label3, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label4, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label5, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label6, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label7, 0 ,0, hdr.ipv4.ttl};

        hdr.mpls.push_front(1);
        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label8, 0 ,0, hdr.ipv4.ttl};
    }

    action mpls_pop() {

        hdr.mpls[0].setInvalid();
        hdr.mpls.pop_front(1);
    }

    action mpls_forward(macAddr_t dstAddr, egressSpec_t port) {

        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;

        hdr.mpls[1].ttl = hdr.mpls[0].ttl - 1;

    }

    action mpls_pop_and_forward(macAddr_t dstAddr, egressSpec_t port) {

        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;

        hdr.mpls[1].ttl = hdr.mpls[0].ttl - 1;
        mpls_pop();
    }

    action drop() {

        mark_to_drop(standard_metadata);
    }

    action mpls_finish() {

        hdr.ethernet.etherType = TYPE_IPV4;
        hdr.ipv4.setValid();
        hdr.ipv4.ttl = hdr.mpls[0].ttl; //MARK not decrease
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {

        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action update_flowlet_id() {
        meta.flowlet_id = meta.flowlet_id + 1;
        flowlet_to_id.write(meta.hash_index, meta.flowlet_id);
    }

    action read_flowlet_registers() {
        //read the registers using the flowlet index you get from hashing the 5-tuple.
        // hash(
        //     meta.hash_index,
	    //     HashAlgorithm.crc16,
	    //     (bit<32>)0,
        //     { 
        //         hdr.ipv4.srcAddr,
        //         hdr.ipv4.dstAddr,
        //         hdr.tcp.srcPort,
        //         hdr.tcp.dstPort,
        //         hdr.ipv4.protocol
        //     },
	    //     (bit<32>)REGISTER_SIZE
        // );
        hash(
            meta.hash_index,
	        HashAlgorithm.crc16,
	        (bit<32>)0,
            { 
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                hdr.tcp.srcPort,
                hdr.tcp.dstPort,
                hdr.ipv4.protocol
            },
	        (bit<32>)REGISTER_SIZE
        );

        flowlet_to_id.read(meta.flowlet_id, meta.hash_index);
        
    }
    

    action ecmp_group(bit<14> ecmp_group_id, bit<16> num_nhops) {

        meta.ecmp_group_id = ecmp_group_id;
        read_flowlet_registers();
        //hash(output_field, (crc16 or crc32), (bit<1>)0, {fields to hash}, (bit<16>)modulo)
        //five tuple: src ip, dst ip, src port, dst port, protocol
        
        // hash(meta.ecmp_hash,
	    // HashAlgorithm.crc16,
	    // (bit<1>)0,
	    // { 
        //     hdr.ipv4.srcAddr,
	    //     hdr.ipv4.dstAddr,
        //     hdr.tcp.srcPort,
        //     hdr.tcp.dstPort,
        //     hdr.ipv4.protocol,
        //     meta.flowlet_id
        // },
	    // num_nhops);
        
        if (meta.flowlet_id == num_nhops) {
            meta.flowlet_id = 0;
        }
       
        meta.ecmp_hash = (bit<14>)meta.flowlet_id;
        update_flowlet_id();
        
    }

    action mpls_forward_and_firewall_active(macAddr_t dstAddr, egressSpec_t port) {
        meta.firewall = (bit<1>) 1;
        mpls_forward(dstAddr, port);
    }

    /* ******************* ipv4 Forward ******************* */
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            NoAction;
        }
        default_action = NoAction;
        size = TABLE_SIZE;
    }

    /* ******************* mpls header ******************** */
    table FEC_tbl {
        key = {
            hdr.ipv4.srcAddr: lpm;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            mpls_ingress_1_hop;
            mpls_ingress_2_hop;
            mpls_ingress_3_hop;
            mpls_ingress_4_hop;
            mpls_ingress_5_hop;
            mpls_ingress_6_hop;
            mpls_ingress_7_hop;
            mpls_ingress_8_hop;
            ecmp_group;
            drop; //UPDATE
            NoAction;
        }
        default_action = NoAction;
        size = TABLE_SIZE;
    }

    /* ******************* Mpls forward ******************* */
    table mpls_act {
        key = {
            hdr.mpls[0].label: exact;
            hdr.mpls[0].s: exact;
        }
        actions = {
            mpls_forward_and_firewall_active;
            mpls_forward;
            mpls_pop;
            mpls_pop_and_forward;
            mpls_finish;
            drop;
            NoAction;
        }
        default_action = NoAction;
        size = TABLE_SIZE;
    }
    /* ******************* MPLS function ******************* */
    
    /* ******************* MPLS Load Balance ******************** */
    table ecmp_group_to_nhop {
        key = {
            meta.ecmp_group_id: exact;
            meta.ecmp_hash: exact;
        }
        actions = {
            mpls_ingress_1_hop;
            mpls_ingress_2_hop;
            mpls_ingress_3_hop;
            mpls_ingress_4_hop;
            mpls_ingress_5_hop;
            mpls_ingress_6_hop;
            mpls_ingress_7_hop;
            mpls_ingress_8_hop;
            NoAction;
        }
        default_action = NoAction;
        size = TABLE_SIZE;
    }
    /* ******************* IPv4 FireWall ******************** */
    table firewall_tbl {
        key = {
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        default_action = NoAction;
        size = TABLE_SIZE;
    }
    apply {
        //Try add mpls header
        if (hdr.ipv4.isValid()) {
            switch (FEC_tbl.apply().action_run){
                ecmp_group: {
                    ecmp_group_to_nhop.apply();
                }
            }
        }

        //mpls forward
        if (hdr.mpls[0].isValid()) {
            mpls_act.apply();

            //MARK 其实检查一下动作也ok
            if (meta.firewall == (bit<1>)1) {
                if(firewall_tbl.apply().hit) {
                    return;//drop
                }
            }
            //Network Service basd on mpls label
            mpls_pop();
        }

        //ipv4 forward
        if (hdr.ipv4.isValid() && !hdr.mpls[0].isValid()){
            ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;