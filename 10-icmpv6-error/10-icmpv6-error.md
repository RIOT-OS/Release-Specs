## Goal: Check single-hop ICMP connectivity over IPv6

*Note: This task requires to send some very specificly formated IPv6 packets. We
recommend to use [scapy] for the construction of those packets in those tests. A
packet can be sent e.g. using (you will require root permission for sending
using link-layer frames with `sendp()`)*

```py
sendp(Ether(dst=DST_HWADDR) / IPv6(src=SRC_IPV6, dst=DST_IPV6) / \
      UDP(dport=DST_PORT) / PAYLOAD_BYTE_STR,
      iface="tapbr0")
```

Testing procedure setup
=======================
All sub-tasks within this specification can be done using one `native` instance
of the `gnrc_networking` example. For the testing process it is assumed running

    $ ./dist/tools/tapsetup/tapsetup

was used to create the TAP interface (including a bridge) required for the
example. As a consequence, when talking about configuring the interface all
Linux-side configuration is assumed to be done on the bridge `tapbr0`. The
interface name might differ if you created it otherwise.

The interface and native instance are assumed to be reset (and if necessary
rebuild) for every task.

Returned packets can be verified using a sniffing tool like Wireshark or
[scapy].

Task #01 - Destination unreachable - no route to destination
============================================================
### Description

Solicit **Destination unreachable - no route to destination** by sending a UDP
to a global address via a native node from a Linux host with global address.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* Sender Address:       beef::1/64 (assigned to interface of Linux host,
                        route to `beef::/64` configured on native node)
* Destination Address:  affe::1/64 (route configured on Linux host, but not
                        on native node)


### Testing procedure

1. Add `beef::1/64` to the TAP interface:

        # ip addr add beef::1/64 dev tapbr0

2. Add `affe::/64` route via the native instance on Linux host side:

        # ip route add affe::/64 via "<native link local IPv6 address>" \
                dev tapbr0

3. Add `beef::/64` route via TAP interface on RIOT side:

        > nib route add 6 beef::/64 "<TAP interface link-local IPv6 address>"

4. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 0 - no route to destination) message
should be sent by the native node.

Task #02 - Destination unreachable - Beyond scope of source address
===================================================================
### Description

Solicit **Destination unreachable - beyond scope of source address** by sending
a UDP to a global address via a native node from a Linux host with link-local
address.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* Sender Address:       Link-local unicast (fe80::.../64)
* Destination Address:  affe::1 (not assigned to an interface of the native
                        node)

### Testing procedure

1. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 2 - beyond scope of source address)
message should be sent by the native node.

Task #03 - Destination unreachable - address unreachable (target node address)
==============================================================================
### Description

Solicit **Destination unreachable - address unreachable** by sending a UDP to an
address not assigned to an interface of the native node from a Linux host.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* Sender Address:       Link local unicast (fe80::.../64)
* Destination Address:  fe80::1 (not assigned to an interface of the native
                        node)

### Testing procedure

1. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 3 - address unreachable) message should
be sent by the native node.

Task #04 - Destination unreachable - address unreachable (neighbor cache miss)
==============================================================================
### Description

Solicit **Destination unreachable - address unreachable** by sending a UDP to a
misconfigured route on the native node from a Linux host.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* Sender Address:       beef::1/64 (assigned to interface of Linux host,
                        route to `beef::/64` configured on native node)
* Destination Address:  affe::1/64 (route configured on Linux host and on native
                        node, the latter to a non-existing neighbor)

### Testing procedure

1. Add `beef::1/64` to the TAP interface:

        # ip addr add beef::1/64 dev tapbr0

2. Add `affe::/64` route via the native instance on Linux host side:

        # ip route add affe::/64 via "<native link local IPv6 address>" \
                dev tapbr0

3. Add `beef::/64` route via TAP interface on RIOT side:

        > nib route add 6 beef::/64 "<TAP interface link-local IPv6 address>"

4. Add `affe::/64` route via not existing node `fe80::1` on RIOT side:

        > nib route add 6 affe::/64 "fe80::1"

5. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 3 - address unreachable) message should
be sent by the native node.

Task #05 - Destination unreachable - port unreachable
=====================================================
### Description

Solicit **Destination unreachable - port unreachable** by sending a UDP to a
native node from a Linux host.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* Sender Address:       Link local unicast (fe80::.../64)
* Destination Address:  Link local unicast (fe80::.../64)

### Testing procedure

1. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 4 - port unreachable) message should be
sent by the native node.

Task #06 - Destination unreachable - port unreachable (large payload)
=====================================================================
### Description

Solicit **Destination unreachable - port unreachable** by sending a UDP just
fitting the MTU of the link to a native node from a Linux host.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          1452B
* Sender Address:       Link local unicast (fe80::.../64)
* Destination Address:  Link local unicast (fe80::.../64)

### Testing procedure

1. Send the UDP packet as specified.

### Result

An ICMPv6 destination unreachable (code: 4 - port unreachable) message should be
sent by the native node. The payload of the original packet carried in the
ICMPv6 message should be truncated to fit the TAP interface's MTU.

Task #07 - Packet too big
=========================
### Description

Solicit **Packet too big** by sending a UDP just fitting the MTU of the first
hop link but not the second hop link via a native node from a Linux host.
* Stack configuration:  6LoWPAN border route(incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          1452B
* Sender Address:       beef::1/64 (assigned to interface of Linux host,
                        route to `beef::/64` configured on native node)
* Destination Address:  affe::1/64 (route configured on Linux host and on native
                        node)

### Testing procedure

1. Add `beef::1/64` to the TAP interface:

        # ip addr add beef::1/64 dev tapbr0

2. Add `affe::/64` route via the native instance on Linux host side:

        # ip route add affe::/64 via "<native link local IPv6 address>" \
                dev tapbr0

3. Compile `gnrc_networking` for `native` with `socket_zep` module

        $ GNRC_NETIF_NUMOF=2 USEMODULE=socket_zep \
          TERMFLAGS="-z [::]:17755 tap0" \
            make -C examples/gnrc_networking clean all term

4. Add `beef::/64` route via TAP interface on RIOT side:

        > nib route add 7 beef::/64 "<TAP interface link-local IPv6 address>"

5. Add `affe::/64` route via not existing node `fe80::1` on RIOT side:

        > nib route add 8 affe::/64 "fe80::1"

6. Send the UDP packet as specified.

### Result

An ICMPv6 packet too big (code: 0) message should be sent by the native node.
The MTU field of the ICMPv6 packet too big message must have a value of 1280.
The payload of the original packet carried in the ICMPv6 message should be
truncated to fit the TAP interface's MTU.

Task #08 - Time exceeded - hop limit exceeded in transit
========================================================
### Description

Solicit **Time exceeded - hop limit exceeded in transit** by sending a UDP just
fitting the MTU of the link to a native node from a Linux host.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* IPv6 hop limit:       1
* Sender Address:       beef::1/64 (assigned to interface of Linux host,
                        route to `beef::/64` configured on native node)
* Destination Address:  affe::1/64 (route configured on Linux host and on native
                        node)

### Testing procedure

1. Add `beef::1/64` to the TAP interface:

        # ip addr add beef::1/64 dev tapbr0

2. Add `affe::/64` route via the native instance on Linux host side:

        # ip route add affe::/64 via "<native link local IPv6 address>" \
                dev tapbr0

3. Add `beef::/64` route via TAP interface on RIOT side:

        > nib route add 6 beef::/64 "<TAP interface link-local IPv6 address>"

4. Add `affe::/64` route via not existing node `fe80::1` on RIOT side:

        > nib route add 6 affe::/64 "fe80::1"

5. Send the UDP packet as specified.

### Result

An ICMPv6 time exceeded (code: 0 - hop limit exceeded in transit) message should
be sent by the native node.

Task #09 - Parameter problem - erroneous header field encountered
=================================================================
### Description

Solicit **Destination unreachable - erroneous header field encountered** by
sending a UDP native node from a Linux host with the IPv6 payload length set to
to large a value.
* Stack configuration:  IPv6 (incl. ICMPv6 error)
* UDP Port:             48879 (no server on native node)
* UDP Payload:          0B
* IPv6 payload length:  20B
* Sender Address:       Link local unicast (fe80::.../64)
* Destination Address:  Link local unicast (fe80::.../64)

### Testing procedure

1. Send the UDP packet as specified.

### Result

An ICMPv6 parameter problem (code: 0 - erroneous header field encountered)
message should be sent by the native node. The pointer field of the error
message should point to the IPv6 payload length field.

Task #10 - IPv6-in-IPv6 encapsulation
=====================================
### Description

Carry an ICMPv6 echo request to the node in an encapsulated IPv6 header to a
node; increase number of encapsulated IPv6 headers incrementally to as many IPv6
headers as is possible within the given MTU.
* Stack configuration:  IPv6
* Interval:             1ms
* ICMPv6 Payload:       0B
* Sender Address:       Link local unicast (fe80::.../64)
* Destination Address:  Link local unicast (fe80::.../64)

### Testing procedure

1. Send the ICMPv6 packet as specified.

### Result

\>96% of the echo requests should be replied. There should only be at most one
echo reply to each echo request.

[scapy]: https://scapy.readthedocs.io/en/latest/
