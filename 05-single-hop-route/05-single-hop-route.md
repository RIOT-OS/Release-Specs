## Goal: Check static routing of ICMPv6 packets over a single hop

Task #01
========
### Description

ICMPv6 echo request/reply exchange between two native nodes with global unicast
addresses. A static default route has to be used (`fibroute add :: via <dst link-local>`).
* Stack configuration: IPv6 (default)
* Count:                  100
* Interval:               10ms
* Payload:                1kB
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.


Task #02
========
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes with global
unicast addresses. The sending node uses global unicast address with a
different prefix. A static default route has to be used (`fibroute add :: via <dst link-local>`).
* Stack configuration: IPv6 (default)
* Count:                  100
* Interval:               10ms
* Payload:                1kB
* Sender address:         affe::1/120
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.

Task #03
========
### Description

ICMPv6 echo request/reply exchange between two native nodes with global unicast
addresses. A static /64 route has to be used (`fibroute add beef::/64 via <dst link-local>`).
* Stack configuration: IPv6 (default)
* Count:                  10
* Interval:               10ms
* Payload:                1kB
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.
