## Goal: Check single-hop UDP connectivity over IPv6

Task #01
========
### Description

Sending UDP between two IoT-LAB_M3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               1s
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<5% packets lost on the receiving node.
