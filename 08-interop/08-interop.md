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

Task #03 - UDP exchange between iotlab-m3 and Contiki
=====================================================
### Description

UDP packet exchange between an iotlab-m3 node running RIOT and a Contiki node.

### Testing procedure
1. Get your hands on a [CC2538DK evaluation board][cc2538dk]
1. Clone the Contiki repository to your machine
   ```sh
   git clone http://github.com/contiki-os/contiki.git && cd contiki/
   ```
2. Go to the `udp-ipv6-echo-server` for the CC2538DK:
   ```sh
   cd examples/cc2538dk/udp-ipv6-echo-server
   ```
3. Apply the following patch
   ```sh
   echo 'diff --git a/examples/cc2538dk/udp-ipv6-echo-server/Makefile b/examples/cc2538dk/udp-ipv6-echo-server/Makefile
   index 5bbbdd6..92ec1c5 100644
   --- a/examples/cc2538dk/udp-ipv6-echo-server/Makefile
   +++ b/examples/cc2538dk/udp-ipv6-echo-server/Makefile
   @@ -1,8 +1,12 @@
   +DEFINES+=PROJECT_CONF_H=\"project-conf.h\"
    CONTIKI_PROJECT = udp-echo-server

    all: $(CONTIKI_PROJECT)

    CONTIKI = ../../..
   +CONTIKI_WITH_RIME = 0
    CONTIKI_WITH_IPV6 = 1
    CFLAGS += -DUIP_CONF_ND6_SEND_NS=1
   +CFLAGS += -DRF_CHANNEL=26
   +CFLAGS += -DIEEE802154_CONF_PANID=0x23
    include $(CONTIKI)/Makefile.include
   diff --git a/examples/cc2538dk/udp-ipv6-echo-server/project-conf.h b/examples/cc2538dk/udp-ipv6-echo-server/project-conf.h
   new file mode 100644
   index 0000000..1718ded
   --- /dev/null
   +++ b/examples/cc2538dk/udp-ipv6-echo-server/project-conf.h
   @@ -0,0 +1,4 @@
   +#ifndef PROJECT_CONF_H_
   +#define PROJECT_CONF_H_
   +#define NETSTACK_CONF_RDC     nullrdc_driver
   +#endif /* PROJECT_CONF_H_ */' | git apply
   ```
4. Build the application with
   ```
   make
   ```
5. **Switch to your RIOT repository**
6. Switch the CC2538DK into bootloader mode by holding SELECT, then pressing
   EM RESET, and then releasing SELECT (there should be no LED blinking when
   you release RESET)
7. Use `dist/tools/cc2538-bsl/cc2538-bsl.py` to flash the *Contiki* application
   to the CC2538DK:
   ```sh
   dist/tools/cc2538-bsl/cc2538-bsl.py -e -w -v -p /dev/ttyUSB1 \
        "<contiki repo>"/examples/cc2538dk/udp-ipv6-echo-server/udp-echo-server.bin
   ```
   *Note:* If you encounter any problems the [cc2538dk] documentation might help
   you.
8. Use either `pyterm` or a sniffer to find out the Contiki node's link local
   address. With the sniffer just copy the source address of the first RPL
   package you see (assuming there are no other IEEE 802.15.4 nodes around you
   😉). With `pyterm` you will see something like

        Rime configured with address 00:12:34:56:78:9a:bc:de

   in the output.

   You might have seen this address also during flashing

        Primary IEEE Address: 00:12:34:56:78:9A:BC:DE

   You can get the IPv6 link local address of the node by toggling the second
   bit of the MSB of the address and prepending `fe80::`. So for the example
   above that would be `fe80::0212:3456:789a:bcde`.
7. For the `iotlab-m3` side just use [gnrc_networking] or the [gnrc_udp] test
   application, whichever you prefer. There start a UDP server on port 3000 with

        > udp server start 3000

   and send a UDP packet to port 3000 of the CC2538DK/Contiki node:

        > udp send <contiki ll-addr> 3000 <data>

   Every packet you send should be echoed by the CC2538DK/Contiki node and
   printed to the console (you might need to send more than once since the
   neighbor discovery of Contiki is not queueing packets for unknown
   destinations).

[cc2538dk]: http://doc.riot-os.org/group__boards__cc2538dk.html
[gnrc_networking]: https://github.com/RIOT-OS/RIOT/tree/master/examples/gnrc_networking
[gnrc_udp]: https://github.com/RIOT-OS/RIOT/tree/master/examples/gnrc_networking

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

Task #08 - UDP between GNRC and lwIP on iotlab-m3
=================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with lwIP (in
both directions).

Task #09 - UDP between GNRC and emb6 on iotlab-m3
=================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with emb6.


Task #10 - UDP between lwIP and emb6 on iotlab-m3
=================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with lwIP and an iotlab-m3 node running RIOT with emb6 (in
both directions).
