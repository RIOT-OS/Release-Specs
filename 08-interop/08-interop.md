## Goal: Test interoperability of gnrc with different implementations

Task #01 - ICMPv6 echo between native and Linux
===============================================
### Description

ICMPv6 echo request/reply exchange between a RIOT native node and the Linux
host.

Task #02 - ICMPv6 echo between iotlab-m3 and Linux with 6LowPAN
===============================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
a Raspberry Pi running Linux with 6LoWPAN support.

Task #03 - ICMPv6 echo between iotlab-m3 and Contiki
====================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
a Contiki node.

Task #04 - ICMPv6 echo between iotlab-m3 and Internet host through Linux with 6LowPAN
=====================================================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a Raspberry Pi running Linux with 6LoWPAN support
as border router. Routes are configured statically.

Since Linux' 6Lo implementation doesn't support 6Lo-ND DAD yet, the RIOT image
needs to be compiled with `CFLAGS += -DGNRC_IPV6_NIB_CONF_SLAAC=1` to be able to
fall back to classic SLAAC + DAD.

Task #05 - ICMPv6 echo between iotlab-m3 and Internet host through RIOT border router
=====================================================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a RIOT node  as border router. Routes are
configured statically.

Task #06 - UDP between iotlab-m3 and Internet host through RIOT border router
=============================================================================
### Description

UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3 node running
RIOT with GNRC and an Linux Internet host using a RIOT node as border router.
Routes are configured statically.

Task #07 - UDP between iotlab-m3 and Internet host through RIOT border router (200b payload)
============================================================================================
### Description

UDP over IPv6 packet exchange (payload length 200) between an iotlab-m3 node
running RIOT with GNRC and an Linux Internet host using a RIOT node as border
router. Routes are configured statically.

Task #08 - UDP between GNRC and lwIP on iotlab-m3 (not working)
===============================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with lwIP (in
both directions).

Task #09 - UDP between GNRC and emb6 on iotlab-m3
=================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with emb6.


Task #10 - UDP between lwIP and emb6 on iotlab-m3 (not working)
===============================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with lwIP and an iotlab-m3 node running RIOT with emb6 (in
both directions).
