## Goal: Check single-hop ICMP connectivity over IPv6

Task #01 - ICMPv6 link-local echo with iotlab-m3
================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               10ms
* Payload:                0B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #02 - ICMPv6 multicast echo with iotlab-m3/samr21-xpro
===========================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #03 - ICMPv6 echo with large payload
=========================================
### Description

ICMPv6 echo request/reply exchange between two nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               100ms
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #04 - ICMPv6 echo with iotlab-m3/samr21-xpro 15 minutes
============================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  10000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #05 (Experimental) - ICMPv6 multicast echo with samr21-xpro/remote
=======================================================================
### Description

ICMPv6 echo request/reply exchange between  a Zolertia Remote node (CC2538) and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #06 (Experimental) - ICMPv6 link-local echo with samr21-xpro/remote
========================================================================
### Description

ICMPv6 echo request/reply exchange between a Zolertia Remote node (CC2538) and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #07 (Experimental) - ICMPv6 multicast echo with samr21-xpro/zero + xbee
============================================================================
### Description

ICMPv6 echo request/reply exchange between an Arduino Zero + XBee node and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #08 (Experimental) - ICMPv6 echo with samr21-xpro/zero + xbee 15 minutes
=============================================================================
### Description

ICMPv6 echo request/reply exchange between an Arduino Zero + XBee node and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.
