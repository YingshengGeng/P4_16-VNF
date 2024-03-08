
#include <core.p4>
#include <v1model.p4>


#define BLOOM_FILTER_ENTRIES 4096
#define BLOOM_FILTER_BIT_WIDTH 1
#define REGISTER_SIZE 8192
#define ID_WIDTH 16

const bit<16> TYPE_IPV4 = 0x0800;
/* Ethernet type for MPLS protocol */
const bit<16> TYPE_MPLS = 0x8847;

/* test size */
#define TABLE_SIZE          256
#define CONST_MAX_LABELS 	128
#define CONST_MAX_MPLS_HOPS 8


#define SKETCH_BUCKET_LENGTH 4096
#define SKETCH_CELL_BIT_WIDTH 32

#define SKETCH_REGISTER(num) register<bit<SKETCH_CELL_BIT_WIDTH>>(SKETCH_BUCKET_LENGTH) sketch##num

// #define SKETCH_READ(num, algorithm) hash(meta.index_sketch##num, HashAlgorithm.algorithm, (bit<16>)0, {hdr.ipv4.srcAddr, \
//  hdr.ipv4.dstAddr, hdr.tcp.srcPort, hdr.tcp.dstPort, hdr.ipv4.protocol}, (bit<32>)SKETCH_BUCKET_LENGTH);\
//  sketch##num.read(meta.value_sketch##num, meta.index_sketch##num);

#define SKETCH_READ(num, algorithm) hash(meta.index_sketch##num, HashAlgorithm.algorithm, (bit<16>)0, {hdr.ipv4.srcAddr, \
 hdr.ipv4.dstAddr}, (bit<32>)SKETCH_BUCKET_LENGTH);\
 sketch##num.read(meta.value_sketch##num, meta.index_sketch##num);
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<20> label_t;
typedef bit<16> hostPort_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

/* mpls header */
header mpls_t {
    bit<20> label;
    bit<3>  exp;
    bit<1>  s;
    bit<8>  ttl;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct metadata {
    bit<2> direction_token;
    bit<14> ecmp_hash;
    bit<14> ecmp_group_id;
    bit<32> hash_index;
    bit<16> flowlet_id;
    bit<1> firewall;
    
    bit<32>value_sketch0;
    bit<32>index_sketch0;
    bit<32>value_sketch1;
    bit<32>index_sketch1;
    bit<32>value_sketch2;
    bit<32>index_sketch2;
}

struct headers {
    ethernet_t                      ethernet;
    /* mpls header */
    mpls_t[CONST_MAX_MPLS_HOPS]     mpls;
    ipv4_t                          ipv4;
    tcp_t                           tcp;
}