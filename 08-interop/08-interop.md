## Goal: Test interoperability of gnrc with different implementatiosn

Task #01
========
### Description

ICMPv6 echo request/reply exchange between a RIOT native node and the Linux
host.

Task #02
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
a Raspberry Pi running Linux with 6LoWPAN support.

Task #03
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
a Contiki node.


Task #04
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a Raspberry Pi running Linux with 6LoWPAN support
as border router. Routes are configured statically.

Task #05
========
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a RIOT node  as border router. Routes are
configured statically.

Task #06
========
### Description

UDP/IPv6 packet exchange (payload length 8) between an iotlab-m3 node running
RIOT with GNRC and an Linux Internet host using a RIOT node as border router.
Routes are configured statically.

Task #07
========
### Description

UDP/IPv6 packet exchange (payload length 200) between an iotlab-m3 node
running RIOT with GNRC and an Linux Internet host using a RIOT node as border
router. Routes are configured statically.

Task #08
========
### Description

Link-local UDP/IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with lwIP.

Task #09
========
### Description

Link-local UDP/IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with emb6.


Task #10
========
### Description

Link-local UDP/IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with lwIP and an iotlab-m3 node running RIOT with emb6.
