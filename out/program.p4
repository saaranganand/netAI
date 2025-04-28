```p4
#include <core.p4>
#include <v1model.p4>

const bit<12> TYPE_ETHERNET = 0x800;  
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
 
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header vlan_tag {
    ethernet_t outer_ethernet;
    
    //vlan_id is 12 bits
    bit<12> vlan_id;
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action forward_to_vlan10(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.outer_ethernet.srcAddr = hdr.outer_ethernet.dstAddr;
        hdr.outer_ethernet.dstAddr = dstAddr;
        hdr.vlan_tag.vlan_id = 10;
        hdr.vlan_tag.
    }

    action forward_to_vlan20(macAddr_t dstAddr, egressSpec_t port){
    standard_metadata.egress_spec = port;
    hdr.outer_ethernet.srcAddr = hdr.outer_ethernet.dstAddr;
    hdr.outer_ethernet.dstAddr = dstAddr;
    hdr.vlan_tag.vlan_id = 20;
    hdr.vlan_tag.
    }

    action forward_to_other_vlan(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.outer_ethernet.srcAddr = hdr.outer_ethernet.dstAddr;
        hdr.outer_ethernet.dstAddr = dstAddr;
        header.ingress_vlan_id =  default_action.ingress_vlan_id;
    }

    table vlan_forward {
        key = {
            hdr.outer_ethernet.dstAddr : exact;
        }
        actions = {
            forward_to_vlan10;
            forward_to_vlan20;
            forward_to_other_vlan;
            drop;  
        }
        size = 1024;
        default_action= drop();
    }
    apply {
       if (hdr.outer_ethernet.isValid()) {
          vlan_forward.apply();
       }
    }  
}


control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}


control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
 apply {
  }  
}

control MyDeparser(packet_out packet, in headers hdr) {
   apply {
       packet.emit(hdr.outer_ethernet);
       packet.emit(hdr.vlan_tag);
    }
}

V1Switch( 
    MyParser(),
    MyVerifyChecksum(),
  v  MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;

```

 



