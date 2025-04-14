## Goal: Check single-hop ICMP connectivity over IPv6

Task #01 - ICMPv6 multicast echo on native
==========================================
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  1000
* Interval:               10ms
* Payload:                0
* Destination Address:    ff02::1

### Result

<1% packets lost on the pinging node.

Task #02 - ICMPv6 link-local echo on native
===========================================
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  1000
* Interval:               100ms
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<1% packets lost on the pinging node.

Task #03 - ICMPv6 link-local echo on native (1 hour)
====================================================
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  3600
* Interval:               1s
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<1% packets lost on the pinging node.

Task #04 - ICMPv6 stress test on native (1 hour)
================================================
### Description

Rapid ICMPv6 echo request/reply exchange from 10 host ping applications (same
host, e.g. Linux host) simultaneously to one native node for 1 hour.
* Stack configuration: IPv6 (default)
* Count:                  Infinity
* Interval:               0ms
* Payload:                1452B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

All nodes are still running, reachable, and the packet buffer is empty 10
seconds after completions (use module `shell_cmd_gnrc_pktbuf`).
Packet loss is irrelevant in this stress test.

Task #05 - ICMPv6 stress test on native (neighbor cache stress)
===============================================================
### Description

Rapid ICMPv6 echo request/reply exchange from 10 native nodes simultaneously to
one native node.
* Stack configuration: IPv6 (default)
* Count:                  100000
* Interval:               0ms
* Payload:                1452B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

All nodes are still running, reachable, and the packet buffer is empty 10
seconds after completions (use module `shell_cmd_gnrc_pktbuf`).
Packet loss is irrelevant in this stress test.

Task #06 - ICMPv6 link-local echo on native (IPv6 fragmentation)
================================================================
### Description

ICMPv6 echo request/reply exchange between two native nodes (make sure module
`gnrc_ipv6_ext_frag` is included and the packet buffer is large enough to handle
both the fragmented and reassembled requests/replies).
* Stack configuration: IPv6 (default)
* Count:                  1000
* Interval:               100ms
* Payload:                2kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<1% packets lost on the pinging node.

Task #07 - ICMPv6 stress test on native64 (1 hour)
================================================
### Description

Rapid ICMPv6 echo request/reply exchange from 10 host ping applications (same
host, e.g. Linux host) simultaneously to one native64 node for 1 hour.
* Stack configuration: IPv6 (default)
* Count:                  Infinity
* Interval:               0ms
* Payload:                1452B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

All nodes are still running, reachable, and the packet buffer is empty 10
seconds after completions (use module `shell_cmd_gnrc_pktbuf`).
Packet loss is irrelevant in this stress test.
