## Goal: Check multi-hop connectivity over IPv6

Task #01
========
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with static routes.

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #02
========
### Description

Sending UDP between two iotlab-m3 nodes over three hops with static routes.

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #03
========
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes over three hops
with RPL generated routes.

### Result

<20% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #04
========
### Description

Sending UDP between two iotlab-m3 nodes over three hops with RPL generated routes.

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
