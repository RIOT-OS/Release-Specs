## Goal: Check static routing of ICMPv6 packets over a single hop

Task #01 - ICMPv6 echo unicast addresess on native (default route)
==================================================================
### Description

ICMPv6 echo request/reply exchange between two native nodes both with global
unicast addresses. A static default route has to be used
(`nib route add <iface> :: <dst link-local>`, also remember to deactivate router
advertisements on both ends *beforehand* with `ifconfig <iface> -rtr_adv`,
otherwise default routes and address resolution will be auto-configured).
* Stack configuration: IPv6 (default)
* Count:                  100
* Interval:               10ms
* Payload:                1kB
* Sender Address:         beef::2/64
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.
No leaks in the packet buffer (check with `shell_cmd_gnrc_pktbuf`).


Task #02 - ICMPv6 echo unicast addresess on iotlab-m3 (default route)
=====================================================================
### Description
https://github.com/RIOT-OS/Release-Specs.git
ICMPv6 echo request/reply exchange between two iotlab-m3 nodes with global
unicast addresses. The sending node uses global unicast address with a
different prefix. A static default route has to be used
(`nib route add <iface> :: <dst link-local>`, *do not* deactivate router
advertisements for this task).
* Stack configuration: IPv6 (default)
* Count:                  100
* Interval:               300ms
* Payload:                1kB
* Sender address:         affe::1/120
* Destination Address:    beef::1/64

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `shell_cmd_gnrc_pktbuf`).

Task #03 - ICMPv6 echo unicast addresess on native64 (default route)
====================================================================
### Description

ICMPv6 echo request/reply exchange between two native64 nodes both with global
unicast addresses. A static default route has to be used
(`nib route add <iface> :: <dst link-local>`, also remember to deactivate router
advertisements on both ends *beforehand* with `ifconfig <iface> -rtr_adv`,
otherwise default routes and address resolution will be auto-configured).
* Stack configuration: IPv6 (default)
* Count:                  100
* Interval:               10ms
* Payload:                1kB
* Sender Address:         beef::2/64
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.
No leaks in the packet buffer (check with `shell_cmd_gnrc_pktbuf`).


Task #04 - ICMPv6 echo unicast addresess on native (specific route)
===================================================================
### Description

ICMPv6 echo request/reply exchange between two native nodes both with global
unicast addresses. A static /64 route has to be used
(`nib route add <iface> beef::/64 <dst link-local>`, also remember to deactivate
router advertisements on both ends *beforehand* with `ifconfig <iface> -rtr_adv`,
otherwise default routes and address resolution will be auto-configured ).
* Stack configuration: IPv6 (default)
* Count:                  10
* Interval:               10ms
* Payload:                1kB
* Sender Address:         beef::2/64
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.
No leaks in the packet buffer (check with `shell_cmd_gnrc_pktbuf`).

Task #05 - ICMPv6 echo unicast addresess on iotlab-m3 (static route)
====================================================================
### Description

ICMPv6 echo request/reply exchange between two native nodes. The source address of the
pinging node should be the local unicast address. To achive this, simply don't
set up a global address on the pinging node. A static default route has to be used
(`nib route add <iface> :: <dst link-local>`, also remember to deactivate
router advertisements on both ends *beforehand* with `ifconfig <iface> -rtr_adv`,
otherwise default routes and address resolution will be auto-configured ).
* Stack configuration: IPv6 (default)
* Count:                  10
* Interval:               300ms
* Payload:                1kB
* Destination Address:    beef::1/64

### Result

<1% packets lost on the pinging node.
