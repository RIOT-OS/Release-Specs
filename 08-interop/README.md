## Goal: Test interoperability of gnrc with different implementations

Task #01 - ICMPv6 echo between native and Linux
===============================================
### Description

ICMPv6 echo request/reply exchange between a RIOT native node and the Linux
host.

Task #02 - ICMPv6 echo between native64 and Linux
===============================================
### Description

ICMPv6 echo request/reply exchange between a RIOT native64 node and the Linux
host.

Task #03 - ICMPv6 echo between iotlab-m3 and Linux with 6LowPAN
===============================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
a Raspberry Pi running Linux with 6LoWPAN support.

Task #04 - ICMPv6 echo between RIOT and Contiki-NG
=====================================================
### Description

ICMPv6 echo request/reply exchange between a node running RIOT and a Contiki node.

### Testing procedure
This assummes Docker is installed and configured. The steps for configuring
Contiki-NG are based on the [official documentation](https://docs.contiki-ng.org/en/master/doc/getting-started/index.html)

1. Clone Contiki-NG

```bash
git clone https://github.com/contiki-ng/contiki-ng.git
cd contiki-ng
git submodule update --init --recursive

```

2. Pull the Contiki-NG Docker image

```bash
docker pull contiker/contiki-ng
```

3. Create a `contiker` alias to start the Contiki-NG environment
```bash

export CNG_PATH=<absolute-path-to-your-contiki-ng>
alias contiker="docker run --privileged --sysctl net.ipv6.conf.all.disable_ipv6=0 --mount type=bind,source=$CNG_PATH,destination=/home/user/contiki-ng -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/bus/usb:/dev/bus/usb -ti contiker/contiki-ng"

```

4. Add the `shell` service to the `examples/hello-world` application.
```diff
diff --git a/examples/hello-world/Makefile b/examples/hello-world/Makefile
index 0a79167ae..710496368 100644
--- a/examples/hello-world/Makefile
+++ b/examples/hello-world/Makefile
@@ -1,5 +1,7 @@
 CONTIKI_PROJECT = hello-world
 all: $(CONTIKI_PROJECT)
 
+MODULES += os/services/shell
+
 CONTIKI = ../..
 include $(CONTIKI)/Makefile.include
```

5. Run the Contiki-NG environment using the `contiker` alias.

```bash
contiker
```
6. Compile the `hello-world` application for your target platform. Check the
[platform documentation](https://docs.contiki-ng.org/en/master/doc/platforms/index.html)
for board specific steps. E.g for `nrf52840dk`:
```
make -C examples/hello-world TARGET=nrf52840 hello-world
make -C examples/hello-world TARGET=nrf52840 hello-world.upload
```

7. Use any serial terminal (e.g `pyterm`) to get the link-local IP address of
the Contiki-NG node:
```
ip-addr
2023-04-14 15:23:36,732 # #f4ce.36c6.d8d1.e340> Node IPv6 addresses:
2023-04-14 15:23:36,735 # -- fe80::f6ce:36c6:d8d1:e340
```

8. For the RIOT side just use [gnrc_networking](https://github.com/RIOT-OS/RIOT/tree/master/examples/gnrc_networking). Get the link-local IP address with `ifconfig`:

```
2023-04-14 15:11:12,614 # ifconfig
2023-04-14 15:11:12,620 # Iface  6  HWaddr: 06:EE  Channel: 26  NID: 0xabcd  PHY: O-QPSK 
2023-04-14 15:11:12,622 #           
2023-04-14 15:11:12,626 #           Long HWaddr: 00:04:25:19:18:01:86:EE 
2023-04-14 15:11:12,633 #            TX-Power: 0dBm  State: IDLE  max. Retrans.: 3  CSMA Retries: 4 
2023-04-14 15:11:12,640 #           AUTOACK  ACK_REQ  CSMA  L2-PDU:102  MTU:1280  HL:64  RTR  
2023-04-14 15:11:12,643 #           RTR_ADV  6LO  IPHC  
2023-04-14 15:11:12,646 #           Source address length: 8
2023-04-14 15:11:12,649 #           Link type: wireless
2023-04-14 15:11:12,655 #           inet6 addr: fe80::204:2519:1801:86ee  scope: link  VAL
2023-04-14 15:11:12,665 #           inet6 group: ff02::2
2023-04-14 15:11:12,668 #           inet6 group: ff02::1
2023-04-14 15:11:12,672 #           inet6 group: ff02::1:ff01:86ee
2023-04-14 15:11:12,674 #           inet6 group: ff02::1a
2023-04-14 15:11:12,675 #           
2023-04-14 15:11:12,678 #           Statistics for Layer 2
2023-04-14 15:11:12,682 #             RX packets 16174  bytes 1812690
2023-04-14 15:11:12,688 #             TX packets 14824 (Multicast: 82)  bytes 1715052
2023-04-14 15:11:12,692 #             TX succeeded 14694 errors 130
2023-04-14 15:11:12,694 #           Statistics for IPv6
2023-04-14 15:11:12,698 #             RX packets 3194  bytes 1453638
2023-04-14 15:11:12,704 #             TX packets 2545 (Multicast: 82)  bytes 1430068
2023-04-14 15:11:12,707 #             TX succeeded 2545 errors 0
2023-04-14 15:11:12,707 # 
```

9. Set the PAN ID of the RIOT node to `abcd` (default PAN ID of Contiki)

```
ifconfig 6 set pan_id abcd
```

10. Run the `ping` command on both the RIOT and the Contiki-NG node:

Contiki-NG:
```
ping fe80::204:2519:1801:86ee
2023-04-14 15:23:29,960 # #f4ce.36c6.d8d1.e340> Pinging fe80::204:2519:1801:86ee
2023-04-14 15:23:29,974 # Received ping reply from fe80::204:2519:1801:86ee, len 4, ttl 64, delay 15 ms
```

RIOT
```
ping fe80::f6ce:36c6:d8d1:e340
2023-04-14 15:30:20,415 # ping fe80::f6ce:36c6:d8d1:e340
2023-04-14 15:30:20,449 # 12 bytes from fe80::f6ce:36c6:d8d1:e340%6: icmp_seq=0 ttl=64 rssi=-46 dBm time=24.320 ms
2023-04-14 15:30:21,441 # 12 bytes from fe80::f6ce:36c6:d8d1:e340%6: icmp_seq=1 ttl=64 rssi=-46 dBm time=6.031 ms
2023-04-14 15:30:22,455 # 12 bytes from fe80::f6ce:36c6:d8d1:e340%6: icmp_seq=2 ttl=64 rssi=-46 dBm time=8.237 ms
2023-04-14 15:30:22,455 # 
2023-04-14 15:30:22,460 # --- fe80::f6ce:36c6:d8d1:e340 PING statistics ---
2023-04-14 15:30:22,465 # 3 packets transmitted, 3 packets received, 0% packet loss
2023-04-14 15:30:22,469 # round-trip min/avg/max = 6.031/12.862/24.320 ms
```

Every packet should be echoed by the target node and printed to the console.

Task #05 - ICMPv6 echo between iotlab-m3 and Internet host through Linux with 6LowPAN
=====================================================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a Raspberry Pi running Linux with 6LoWPAN support
as border router. Routes are configured statically.

Since Linux' 6Lo implementation doesn't support 6Lo-ND DAD yet, the RIOT image
needs to be compiled with `CFLAGS += -DGNRC_IPV6_NIB_CONF_SLAAC=1` to be able to
fall back to classic SLAAC + DAD.

Task #06 - ICMPv6 echo between iotlab-m3 and Internet host through RIOT border router
=====================================================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 node running RIOT and
an Linux Internet host using a RIOT node  as border router. Routes are
configured statically.

Task #07 - UDP between iotlab-m3 and Internet host through RIOT border router
=============================================================================
### Description

UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3 node running
RIOT with GNRC and an Linux Internet host using a RIOT node as border router.
Routes are configured statically.

Task #08 - UDP between iotlab-m3 and Internet host through RIOT border router (200b payload)
============================================================================================
### Description

UDP over IPv6 packet exchange (payload length 200) between an iotlab-m3 node
running RIOT with GNRC and an Linux Internet host using a RIOT node as border
router. Routes are configured statically.

Task #09 - UDP between GNRC and lwIP on iotlab-m3
=================================================
### Description

Link-local UDP over IPv6 packet exchange (payload length 8) between an iotlab-m3
node running RIOT with GNRC and an iotlab-m3 node running RIOT with lwIP (in
both directions).

<!-- Task 09 and 10 used were deprecated, their slots are free to be newly allocated -->

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
   
Task #12 - ICMPv6 echo between Border Router with WiFi uplink to named Internet host
====================================================================================
### Description

This test will ensure RIOT can connect to a real IPv6 enabled WiFi network and
share the uplink connection with constrained nodes.

An esp* board with the `gnrc_border_router` connects to your WiFi.
The module `sock_dns` is used to resolve domain names.
The module `gnrc_ipv6_nib_dns` is used to distribute DNS information through router advertisements.

Two network interfaces are configured:

 - a 802.11 WiFi interface used as uplink
 - a proprietary `esp_now` interface as 6LoWPAN downlink
 
 Materials
---------

You'll need:

 - a pair of esp8266/esp32 boards
 - 2.4 GHz WiFi network with an IPv6 uplink
 - to make sure prefix delegation (IA_PD) is enabled in your router's DHCPv6 server
   (On the popular Fritz!Box line of routers this can be enabled in the
   Network -> Network Settings -> IPv6 Addresses menu. On [OpenWRT](https://openwrt.org/docs/guide-user/network/ipv6/start) it should be enabled by default)

### Details

Flash the `gnrc_border_router` example onto one of the esp* boards.
Use the `sock_dns` and `gnrc_ipv6_nib_dns` modules to enable name resolution.
The credentials for the WiFi network will be passed on the command line.
Replace `esp8266-esp-12x` with the esp* board of your choice, adjust `PORT` if needed.

```
USEMODULE="sock_dns gnrc_ipv6_nib_dns" make -C examples/gnrc_border_router BOARD=esp<...> UPLINK=wifi WIFI_SSID=<your_ssd> WIFI_PASS=<your_password> PORT=<port> flash term
```

### Result

RIOT should be able to connect to your WiFi network and configure a global address on both interfaces

```
2020-08-02 20:38:20,346 # Iface  11  HWaddr: EC:FA:BC:5F:82:91  Channel: 6  Link: up 
2020-08-02 20:38:20,349 #           L2-PDU:1500  MTU:1492  HL:255  RTR  
2020-08-02 20:38:20,352 #           Source address length: 6
2020-08-02 20:38:20,355 #           Link type: wireless
2020-08-02 20:38:20,360 #           inet6 addr: fe80::eefa:bcff:fe5f:8291  scope: link  VAL
2020-08-02 20:38:20,368 #           inet6 addr: 2001:16b8:453f:1f00:eefa:bcff:fe5f:8291  scope: global  VAL
2020-08-02 20:38:20,371 #           inet6 group: ff02::2
2020-08-02 20:38:20,374 #           inet6 group: ff02::1
2020-08-02 20:38:20,377 #           inet6 group: ff02::1:ff5f:8291
2020-08-02 20:38:20,377 #           
2020-08-02 20:38:20,382 # Iface  10  HWaddr: EE:FA:BC:5F:82:91  Channel: 6 
2020-08-02 20:38:20,385 #           L2-PDU:249  MTU:1280  HL:64  RTR  
2020-08-02 20:38:20,390 #           RTR_ADV  6LO  Source address length: 6
2020-08-02 20:38:20,393 #           Link type: wireless
2020-08-02 20:38:20,399 #           inet6 addr: fe80::ecfa:bcff:fe5f:8291  scope: link  VAL
2020-08-02 20:38:20,404 #           inet6 addr: 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291  scope: global  VAL
2020-08-02 20:38:20,407 #           inet6 group: ff02::2
2020-08-02 20:38:20,410 #           inet6 group: ff02::1
2020-08-02 20:38:20,416 #           inet6 group: ff02::1:ff5f:8291
```

You should be able to ping global addresses (requires a working IPv6 uplink on your network)

```
2020-08-02 20:35:27,462 # ping 2600::
2020-08-02 20:35:27,672 # 12 bytes from 2600::: icmp_seq=0 ttl=50 time=203.340 ms
2020-08-02 20:35:28,607 # 12 bytes from 2600::: icmp_seq=1 ttl=50 time=139.033 ms
2020-08-02 20:35:29,608 # 12 bytes from 2600::: icmp_seq=2 ttl=50 time=140.839 ms
2020-08-02 20:35:29,609 # 
2020-08-02 20:35:29,611 # --- 2600:: PING statistics ---
2020-08-02 20:35:29,616 # 3 packets transmitted, 3 packets received, 0% packet loss
2020-08-02 20:35:29,621 # round-trip min/avg/max = 139.033/161.070/203.340 ms
```

Valid DNS names should get resolved too

```
2020-08-02 20:35:37,927 # ping riot-os.org
2020-08-02 20:35:38,075 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=0 ttl=56 time=33.071 ms
2020-08-02 20:35:39,076 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=1 ttl=56 time=34.129 ms
2020-08-02 20:35:40,076 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=2 ttl=56 time=33.182 ms
2020-08-02 20:35:40,076 # 
2020-08-02 20:35:40,078 # --- riot-os.org PING statistics ---
2020-08-02 20:35:40,084 # 3 packets transmitted, 3 packets received, 0% packet loss
2020-08-02 20:35:40,088 # round-trip min/avg/max = 33.071/33.460/34.129 ms
```

Task #13 - ICMPv6 echo between ESP and named Internet host through RIOT BR with 6LowPAN
=======================================================================================
### Description

A second esp* board will connect to the border router from Task #12 using 6LoWPAN/`esp_now`.
It should be able to access hosts on the internet.

### Details

Flash the `gnrc_networking` example onto the second esp* board.
Use the `sock_dns` and `gnrc_ipv6_nib_dns` modules to enable name resolution.
Replace `esp8266-esp-12x` with the esp* board of your choice, adjust `PORT` if needed.

```
USEMODULE="sock_dns gnrc_ipv6_nib_dns" make -C examples/gnrc_networking BOARD=esp<…> PORT=<port> flash term
```

### Result

RIOT should connect to the border router and obtain a global address.
Make sure both boards operate on the same `esp_now` channel.

```
2020-08-02 20:45:02,898 # Iface  9  HWaddr: 3C:71:BF:9E:13:FD  Channel: 6 
2020-08-02 20:45:02,902 #           L2-PDU:249  MTU:1280  HL:64  RTR  
2020-08-02 20:45:02,906 #           RTR_ADV  6LO  Source address length: 6
2020-08-02 20:45:02,909 #           Link type: wireless
2020-08-02 20:45:02,914 #           inet6 addr: fe80::3e71:bfff:fe9e:13fd  scope: link  VAL
2020-08-02 20:45:02,921 #           inet6 addr: 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd  scope: global  VAL
2020-08-02 20:45:02,924 #           inet6 group: ff02::2
2020-08-02 20:45:02,927 #           inet6 group: ff02::1
2020-08-02 20:45:02,930 #           inet6 group: ff02::1:ff9e:13fd
2020-08-02 20:45:02,931 #           
2020-08-02 20:45:02,934 #           Statistics for Layer 2
2020-08-02 20:45:02,937 #             RX packets 0  bytes 0
2020-08-02 20:45:02,942 #             TX packets 0 (Multicast: 0)  bytes 214
2020-08-02 20:45:02,945 #             TX succeeded 3 errors 0
2020-08-02 20:45:02,947 #           Statistics for IPv6
2020-08-02 20:45:02,950 #             RX packets 3  bytes 312
2020-08-02 20:45:02,955 #             TX packets 4 (Multicast: 2)  bytes 264
2020-08-02 20:45:02,958 #             TX succeeded 4 errors 0
```

You should be able to reach the border router using it's global address

```
2020-08-02 20:45:41,423 #  ping 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291
2020-08-02 20:45:41,439 # 12 bytes from 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291: icmp_seq=0 ttl=64 time=8.020 ms
2020-08-02 20:45:42,438 # 12 bytes from 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291: icmp_seq=1 ttl=64 time=7.252 ms
2020-08-02 20:45:43,438 # 12 bytes from 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291: icmp_seq=2 ttl=64 time=6.779 ms
2020-08-02 20:45:43,438 # 
2020-08-02 20:45:43,443 # --- 2001:16b8:453f:1ff0:ecfa:bcff:fe5f:8291 PING statistics ---
2020-08-02 20:45:43,449 # 3 packets transmitted, 3 packets received, 0% packet loss
2020-08-02 20:45:43,453 # round-trip min/avg/max = 6.779/7.350/8.020 ms
```

You should be able to reach a global address on the internet

```
2020-08-02 20:45:49,052 #  ping 2600::
2020-08-02 20:45:49,200 # 12 bytes from 2600::: icmp_seq=0 ttl=49 time=143.513 ms
2020-08-02 20:45:50,200 # 12 bytes from 2600::: icmp_seq=1 ttl=49 time=143.223 ms
2020-08-02 20:45:51,199 # 12 bytes from 2600::: icmp_seq=2 ttl=49 time=142.450 ms
2020-08-02 20:45:51,200 # 
2020-08-02 20:45:51,202 # --- 2600:: PING statistics ---
2020-08-02 20:45:51,207 # 3 packets transmitted, 3 packets received, 0% packet loss
2020-08-02 20:45:51,212 # round-trip min/avg/max = 142.450/143.062/143.513 ms
``` 

DNS names should also get resolved

```
2020-08-02 20:45:57,277 #  ping riot-os.org
2020-08-02 20:45:57,330 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=0 ttl=55 time=35.999 ms
2020-08-02 20:45:58,335 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=1 ttl=55 time=40.993 ms
2020-08-02 20:45:59,328 # 12 bytes from 2a01:4f8:151:64::11: icmp_seq=2 ttl=55 time=34.089 ms
2020-08-02 20:45:59,329 # 
2020-08-02 20:45:59,331 # --- riot-os.org PING statistics ---
2020-08-02 20:45:59,336 # 3 packets transmitted, 3 packets received, 0% packet loss
2020-08-02 20:45:59,340 # round-trip min/avg/max = 34.089/37.027/40.993 ms
```

And finally, you should be able to reach the 6LoWPAN node from any IPv6 host from your local network.

```
% ping -c3 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd
PING 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd(2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd) 56 data bytes
64 bytes from 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd: icmp_seq=1 ttl=63 time=11.0 ms
64 bytes from 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd: icmp_seq=2 ttl=63 time=9.08 ms
64 bytes from 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd: icmp_seq=3 ttl=63 time=10.5 ms

--- 2001:16b8:453f:1ff0:3e71:bfff:fe9e:13fd ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 9.077/10.192/10.997/0.814 ms
```
