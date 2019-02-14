_The following is a possible way to run the tests, this is just an example_
## Goal: Check multi-hop connectivity over IPv6
_We will arrange all 4 nodes in a chain topology:
node1 <-> node2 <-> node3 <-> node4_

### Pre-setup Steps
1. Book 4 [iotlab](https://www.iot-lab.info/testbed/dashboard) M3 nodes

# Task 1 and 2 Setup
1. Open 4 instances of nodes physically close together
`USEMODULE=gnrc_pktbuf_cmd make -C tests/gnrc_udp/ BOARD=iotlab-m3
IOTLAB_NODE=<iotlab id> flash term`
2. On each end of the nodes add a global IP address (ie. node1:`ifconfig 6 add
    abcd::1` and node 4: `ifconfig 6 add abcd::2`)
3. Add the routing for both ways:
- Node 1: `nib route add 6 abcd::2 <ipv6 addr of node 2>`
- Node 2: `nib route add 6 abcd::2 <ipv6 addr of node 3>` and `nib route add 6
abcd::1 <ipv6 addr of node 1>`
- Node 3: `nib route add 6 abcd::2 <ipv6 addr of node 4>` and `nib route add 6
abcd::1 <ipv6 addr of node 2>`
- Node 4: `nib route add 6 abcd::1 <ipv6 addr of node 3>`
3. Proceed to Task specific commands


Task #01 - ICMPv6 echo on iotlab-m3 with three hops (static route)
==================================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with static routes.

1. Follow Task 1 and 2 setup
2. Ping node 4 from node 1, Node 1:`ping6 -c 100 -s 50 -i 100 abcd::2`

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #02 - UDP on iotlab-m3 with three hops (static route)
==========================================================
### Description

Sending UDP between two iotlab-m3 nodes over three hops with static routes.

1. Follow Task 1 and 2 setup
2. Start a udp server on node 1, Node 1:`udp server start 1234`
3. Start a udp server on node 4, Node 4:`udp server start 4321`
4. Send a packet to node 4 from node 1, Node 1:`udp send abcd::2 4321 50 100 100000`
5. Send a packet to node 1 from node 4, Node 4:`udp send abcd::1 1234 50 100 100000`

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).


# Task 3 and 4 Setup
1. Flash all nodes with with the l2filter_whitelist module firmware
`USEMODULE="l2filter_whitelist gnrc_pktbuf_cmd" BOARD=iotlab-m3 IOTLAB_NODE=<iotlab id> make -C tests/gnrc_udp/ flash term`
2. Setup the l2filter_whitelist addresses
- Node 1: `ifconfig 6 l2filter add <MAC addr of node 2>`
- Node 2: `ifconfig 6 l2filter add <MAC addr of node 1>` and `ifconfig 6 l2filter add <MAC addr of node 3>`
- Node 3: `ifconfig 6 l2filter add <MAC addr of node 2>` and `ifconfig 6 l2filter add <MAC addr of node 4>`
- Node 4: `ifconfig 6 l2filter add <MAC addr of node 3>`
3. Add a global IP address, Node 1: `ifconfig 6 add abcd::1/64`
4. Apply rpl root, Node 1: `rpl root 0 abcd::1`
5. Check Node 4 for R >= 1024 indicating more at least 3 hops,  Node 4:

```
> rpl
rpl
instance table: [X]
parent table:   [X]     [ ]     [ ]

instance [0 | Iface: 6 | mop: 2 | ocp: 0 | mhri: 256 | mri 0]
        dodag [abca::1 | R: 1024 | OP: Router | PIO: on | TR(I=[8,20], k=10, c=1, TC=14s)]
                parent [addr: fe80::1711:6b10:65fa:5c0a | rank: 768]
```

Task #03 - ICMPv6 echo on iotlab-m3 with three hops (RPL route)
===============================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with RPL generated routes.

1. Follow Task 3 and 4 setup
2. Ping root node from other node, Node 4:`ping6 -c 100 -s 50 -i 100 abcd::1`

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #04 - UDP on iotlab-m3 with three hops (RPL route)
=======================================================
### Description

Sending UDP between two iotlab-m3 nodes over three hops with RPL generated routes.

1. Follow Task 3 and 4 setup
2. Start a udp server on root node, Node 1:`udp server start 1234`
3. Start a udp server on the other node, Node 4:`udp server start 4321`
4. Send a packet to the other node from the root node, Node 1:`udp send abcd::<other node global address> 4321 50 100 100000`
5. Send a packet to the other node from the root node, Node 4:`udp send abcd::1 1234 50 100 100000`

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
