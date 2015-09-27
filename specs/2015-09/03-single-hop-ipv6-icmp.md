## Goal: Check single-hop ICMP connectivity over IPv6

Task #01
========
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  1000
* Interval:               10ms
* Payload:                0
* Destination Address:    ff02::1

### Result

<1% packets lost on the pinging node.

Task #02
========
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  1000
* Interval:               100ms
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<1% packets lost on the pinging node.

Task #03
========
### Description

ICMPv6 echo request/reply exchange between two native nodes.
* Stack configuration: IPv6 (default)
* Count:                  3600
* Interval:               1s
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<1% packets lost on the pinging node.
