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

Task #02 - UDP on iotlab-m3 (other port)
========================================
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
