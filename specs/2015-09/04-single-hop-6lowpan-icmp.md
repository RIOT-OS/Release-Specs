## Goal: Check single-hop ICMP connectivity over IPv6

Task #01
========
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

Task #02
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a SAMR21 node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #03
========
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

Task #04
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a SAMR21 node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  10000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.
