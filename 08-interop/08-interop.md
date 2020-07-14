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
   to the CC2538DK.
   You first need to fetch it from upstream.
   ```sh
   make -C examples/hello-world/ ${PWD}/dist/tools/cc2538-bsl/cc2538-bsl.py
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

Task #09 - deprecated
=====================

Task #10 - deprecated
=====================

Task #11 - UDP exchange between iotlab-m3 and Zephyr
=====================================================
### Description

UDP packet exchange between an iotlab-m3 node running RIOT and a samr21-xpro
node running Zephyr.

### Testing procedure

#### Setting up the Zephyr node

1. Follow the
['Getting Started'](https://docs.zephyrproject.org/latest/getting_started/index.html)
guide on Zephyr's documentation.
2. You will be using the `echo_server` example application. To compile and
   flash, connect the samr21-xpro board and in zephyr's root directory run:

   ```sh
   west build -p auto -b atsamr21_xpro samples/net/sockets/echo_server -- -DOVERLAY_CONFIG=overlay-802154.conf
   west flash
   ```
3. If everything is OK you should be able to connect to the serial output use
   any terminal program. For example:
   ```sh
   minicom -D /dev/ttyACM0 -o
   ```
4. By pressing tab you should be able to see all available commands. Get the
   node's IPv6 by running the following on its shell:

   ```sh
   # On samr21-xpro:zephyr node
   uart:~$ net ipv6

   IPv6 support                              : enabled
   IPv6 fragmentation support                : disabled
   Multicast Listener Discovery support      : enabled
   Neighbor cache support                    : enabled
   Neighbor discovery support                : enabled
   Duplicate address detection (DAD) support : enabled
   Router advertisement RDNSS option support : enabled
   6lo header compression support            : enabled
   Max number of IPv6 network interfaces in the system          : 1
   Max number of unicast IPv6 addresses per network interface   : 3
   Max number of multicast IPv6 addresses per network interface : 4
   Max number of IPv6 prefixes per network interface            : 2

   IPv6 addresses for interface 0x20007d60 (IEEE 802.15.4)
   =======================================================
   Type            State           Lifetime (sec)  Address
   autoconf        preferred       infinite        fe80::d419:100:7ae4:9b3b/128
   manual          preferred       infinite        2001:db8::1/128
   ```

   Similarly, to get the IEEE 802.15.4 PAN ID and channel, run:

   ```sh
   # On samr21-xpro:zephyr node
   uart:~$ ieee802154 get_pan_id
   PAN ID 43981 (0xabcd)

   uart:~$ ieee802154 get_chan
   Channel 26
   ```

#### Setting up the RIOT node

1. Flash the [gnrc_networking] example or the [gnrc_udp] test to the iotlab-m3 board
   test.
2. Set the channel and PAN ID to the same values as the Zephyr node:
   ```sh
   # On iotlab-m3:riot node
   > ifconfig 6 set chan 26
   ifconfig 6 set chan 26
   success: set channel on interface 6 to 26

   > ifconfig 6 set pan_id 0xabcd
   ifconfig 6 set pan_id 0xabcd
   success: set network identifier on interface 6 to 0xabcd
   ```
3. The UDP echo server application on the Zephyr node will be listening on port
   4242, and echoing to the source port of the incoming packet. As both
   [gnrc_networking] example and [gnrc_udp] test applications use the
   destination port as the source port for the `udp send` command, we need to
   start a server on port 4242:

   ```sh
   # On iotlab-m3:riot node
   > udp server start 4242
   udp server start 4242
   Success: started UDP server on port 4242
   ```
4. Send packets to the echo server in the Zephyr node, they should be echoed and
   printed on the RIOT side. Zephyr node will inform of the received packet as
   well on the shell.

   ```sh
   # On iotlab-m3:riot node
   > udp send fe80::d419:100:7ae4:9b3b 4242 "RIOT Testing!"
   udp send fe80::9c1a:100:42e5:9b3b 4242 "RIOT Testing!"
   Success: sent 13 byte(s) to [fe80::9c1a:100:42e5:9b3b]:4242
   PKTDUMP: data received:
   ~~ SNIP  0 - size:  13 byte, type: NETTYPE_UNDEF (0)
   00000000  52  49  4F  54  20  54  65  73  74  69  6E  67  21
   ~~ SNIP  1 - size:   8 byte, type: NETTYPE_UDP (4)
      src-port:  4242  dst-port:  4242
      length: 21  cksum: 0xee9e
   ~~ SNIP  2 - size:  40 byte, type: NETTYPE_IPV6 (2)
   traffic class: 0x00 (ECN: 0x0, DSCP: 0x00)
   flow label: 0x00000
   length: 21  next header: 17  hop limit: 64
   source address: fe80::9c1a:100:42e5:9b3b
   destination address: fe80::30a9:fa65:106b:1114
   ~~ SNIP  3 - size:  24 byte, type: NETTYPE_NETIF (-1)
   if_pid: 7  rssi: -43  lqi: 255
   flags: 0x0
   src_l2addr: 9E:1A:01:00:42:E5:9B:3B
   dst_l2addr: 32:A9:FA:65:10:6B:11:14
   ~~ PKT    -  4 snips, total size:  85 byte
   ```
