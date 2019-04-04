## Goal: Check single-hop UDP connectivity over IPv6

Task #01 - UDP on iotlab-m3
===========================
### Description

Sending UDP between two iotlab-m3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               1s
* Port:                   1337
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<5% packets lost on the receiving node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #02 - UDP on iotlab-m3 (UDP port compression)
==================================================
### Description

Sending UDP between two iotlab-m3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               1s
* Port:                   61616
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<5% packets lost on the receiving node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #03 - UDP on native (non-existent neighbor)
================================================
### Description

Sending UDP from one native node to a non-existent neighbor.
* Stack configuration:    IPv6 (default)
* Count:                  1000
* Interval:               0us
* Port:                   1337
* Payload:                8B
* Destination Address:    Non-existent link local unicast (e.g fe80::bd:b7ec)

### Result

No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
Packet loss is irrelevant for this test.

Task #04 - UDP on iotlab-m3 (non-existent neighbor)
===================================================
### Description

Sending UDP from one iotlab-m3 node to a non-existent neighbor.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               0us
* Port:                   1337
* Payload:                8B
* Destination Address:    Non-existent link local unicast (e.g fe80::bd:b7ec)

### Result

No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
Packet loss is irrelevant for this test.

Task #05 - Empty UDP on native
==============================
### Description

Sending UDP between two native nodes.
* Stack configuration:    IPv6 (default)
* Count:                  10
* Interval:               100ms
* Port:                   1337
* Payload:                0B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<=10% packets lost on the receiving node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #06 - Empty UDP on iotlab-m3
=================================
### Description

Sending UDP between two iotlab-m3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  10
* Interval:               100ms
* Port:                   1337
* Payload:                0B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<=10% packets lost on the receiving node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
