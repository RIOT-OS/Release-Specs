_The following is a possible way to run the tests, this is just an example_
## Goal: Check multi-hop connectivity over IPv6
_We will arrange all 4 nodes in a chain topology:
node1 <-> node2 <-> node3 <-> node4_

### Pre-setup Steps
1. Book 4 [iotlab](https://www.iot-lab.info/testbed/dashboard) M3 nodes

# Task 1 and 2 Setup
1. First build the firmware for all the nodes
`USEMODULE=shell_cmd_gnrc_pktbuf make -C tests/net/gnrc_udp/ BOARD=iotlab-m3 clean all`
1. Open 4 instances of nodes physically close together
`make -C tests/net/gnrc_udp/ BOARD=iotlab-m3 IOTLAB_NODE=<iotlab id> flash-only term`
1. On each end of the nodes add a global IP address (ie. node1:
   `ifconfig 5 add abcd::1` and node 4: `ifconfig 5 add abcd::2`)
1. Add the routing for both ways:
    - Node 1: `nib route add 5 abcd::2 <ipv6 addr of node 2>`
    - Node 2: `nib route add 5 abcd::2 <ipv6 addr of node 3>` and
              `nib route add 5 abcd::1 <ipv6 addr of node 1>`
    - Node 3: `nib route add 5 abcd::2 <ipv6 addr of node 4>` and
              `nib route add 5 abcd::1 <ipv6 addr of node 2>`
    - Node 4: `nib route add 5 abcd::1 <ipv6 addr of node 3>`
1. Proceed to Task specific commands


Task #01 - ICMPv6 echo on iotlab-m3 with three hops (static route)
==================================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with static routes.

1. Follow Task 1 and 2 setup
2. Ping node 4 from node 1, Node 1:`ping -c 100 -s 50 -i 100 abcd::2`

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `pktbuf`).

Task #02 - UDP on iotlab-m3 with three hops (static route)
==========================================================
### Description

Sending UDP between two iotlab-m3 nodes over three hops with static routes.

1. Follow Task 1 and 2 setup
2. Start a udp server on node 1, Node 1:`udp server start 1234`
3. Start a udp server on node 4, Node 4:`udp server start 4321`
4. Send 100 packets to node 4 from node 1, Node 1:`udp send abcd::2 4321 50 100 100000`
5. Send 100 packets to node 1 from node 4, Node 4:`udp send abcd::1 1234 50 100 100000`

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `pktbuf`).


# Task 3 and 4 Setup
1. First build the firmware for all the nodes
`USEMODULE="l2filter_whitelist shell_cmd_gnrc_pktbuf" BOARD=iotlab-m3 make -C tests/net/gnrc_udp/ clean all`
1. Flash all nodes with with the l2filter_whitelist module firmware
`BOARD=iotlab-m3 IOTLAB_NODE=<iotlab id> make -C tests/net/gnrc_udp/ flash-only term`
1. Setup the l2filter_whitelist addresses
    - Node 1: `ifconfig 5 l2filter add <MAC addr of node 2>`
    - Node 2: `ifconfig 5 l2filter add <MAC addr of node 1>` and
              `ifconfig 5 l2filter add <MAC addr of node 3>`
    - Node 3: `ifconfig 5 l2filter add <MAC addr of node 2>` and
              `ifconfig 5 l2filter add <MAC addr of node 4>`
    - Node 4: `ifconfig 5 l2filter add <MAC addr of node 3>`
    - Node all: `rpl init 5`
1. Add a global IP address, Node 1: `ifconfig 5 add abcd::1/64`
1. Apply rpl root, Node 1: `rpl root 0 abcd::1`
1. Check Node 4 for R >= 1024 indicating more at least 3 hops,  Node 4:

```
> rpl
rpl
instance table: [X]
parent table:   [X]     [ ]     [ ]

instance [0 | Iface: 5 | mop: 2 | ocp: 0 | mhri: 256 | mri 0]
        dodag [abca::1 | R: 1024 | OP: Router | PIO: on | TR(I=[8,20], k=10, c=1, TC=14s)]
                parent [addr: fe80::1711:6b10:65fa:5c0a | rank: 768]
```

Task #03 - ICMPv6 echo on iotlab-m3 with three hops (RPL route)
===============================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with RPL generated routes.

1. Follow Task 3 and 4 setup
1. Ping root node from other node, Node 4:`ping -c 100 -s 50 -i 100 abcd::1`

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `pktbuf`).

Task #04 - UDP on iotlab-m3 with three hops (RPL route)
=======================================================
### Description

Sending UDP between two iotlab-m3 nodes over three hops with RPL generated routes.

1. Follow Task 3 and 4 setup
1. Start a udp server on root node, Node 1:`udp server start 1234`
1. Start a udp server on the other node, Node 4:`udp server start 4321`
1. Send 100 packets to the other node from the root node, Node 1:`udp send abcd::<other node global address> 4321 50 100 100000`
1. Send 100 packets to the other node from the root node, Node 4:`udp send abcd::1 1234 50 100 100000`

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `pktbuf`).

Task #05 (Experimental) - UDP with large payload on iotlab-m3 with three hops (RPL route)
=========================================================================================
### Description

Sending UDP between two iotlab-m3 nodes over three hops with RPL generated routes.

1. Follow Task 3 and 4 setup
1. Start a udp server on root node, Node 1:`udp server start 1234`
1. Start a udp server on the other node, Node 4:`udp server start 4321`
1. Send 60 packets to the other node from the root node, Node 1:`udp send abcd::<other node global address> 4321 2048 60 1000000`
1. Send 60 packets to the other node from the root node, Node 4:`udp send abcd::1 1234 2048 60 1000000`

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `pktbuf`).

_currently pktbuf is OK, sending is successful, but the no packets are received._

