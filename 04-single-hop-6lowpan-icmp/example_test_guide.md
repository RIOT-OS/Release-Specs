_The following is a possible way to run the tests, this is just an example_
## Goal: Check single hop 6lowpan icmp

### Pre-setup Steps
_One can use IoT-LAB for everything but the remote-revb boards_
1. Get 2 of the following boards: `samr21-xpro`, `iotlab-m3`
2. Get the following boards:`remote-revb`, `arduino-zero` with `xbee` module
3. `cd ${RIOTBASE}/tests/net/gnrc_udp`
4. Setup a terminal for each board _(tmux is your friend)_
5. Find the serial numbers and ports with `ls /dev/serial/by-id/` or with
`make -C tests/net/gnrc_udp list-ttys`
6. For the samr21 terminals use the following to setup the env
_eg_ `export BOARD=samr21-xpro && export SERIAL=<SAMR_SERIAL> && export PORT=<SAMR_PORT>`

`export BOARD=samr21-xpro && export SERIAL=ATML2127031800008334 && export PORT=/dev/ttyACM0`

`export BOARD=samr21-xpro && export PORT_=ATML2127031800002161 && export PORT=/dev/ttyACM1`
7. For the remote-revb:
_eg_ `export BOARD=remote-revb && export PORT=<REMOTE_PORT> && export PORT_LINUX=${PORT}`

`export BOARD=remote-revb && export PORT=/dev/ttyUSB0 && export PORT_LINUX=${PORT}`

`export BOARD=remote-revb && export PORT=/dev/ttyUSB1 && export PORT_LINUX=${PORT}`
8. For the iotlab-m3 the flashing must be done when the other is unplugged or
turned off as there is no way to distinguish between nodes:
_eg_ `export BOARD=iotlab-m3 && export PORT=<M3_PORT>`

`export BOARD=iotlab-m3 && export PORT=/dev/ttyUSB3`

`export BOARD=iotlab-m3 && export PORT=/dev/ttyUSB5`
9. Use `make flash term` to access the nodes (or just `make term` if the
firmware is already flashed)

_note: Boards types can be changed to help vary the test coverage_

Task #01 - ICMPv6 link-local echo with iotlab-m3
================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes
1. On the dest node use `ifconfig`
2. Copy the link local address `inet6 addr: fe80::... scope: local VAL`, it
should look like `fe80::1711:6b10:65f8:b43a`
3. Ping from the src to the dest `ping -c 1000 -i 20 -s 0 <ll_addr>`
4. Record the packet loss, it should be less then 10%
_(if packet loss is high try to increase the -i value as it may be a property of
the async ping call)_
5. check the packet buffer with `pktbuf` once everything is complete
_(as long as there is no hex dump it should be fine)_

### Result

<10% packets lost on the pinging node.

Task #02 - ICMPv6 multicast echo with iotlab-m3/samr21-xpro
===========================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.

1. Set the channel on the both dest and src to 17 `ifconfig 6 set chan 17`
2. Ping from the src to the dest `ping -c 1000 -i 100 -s 50 ff02::1`
3. Record the packet loss and timings, it should be less then 10%
4. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #03 - ICMPv6 echo with large payload
=========================================
### Description

ICMPv6 echo request/reply exchange between _any_ two nodes.

1. Ping from the src to the dest `ping -c 500 -i 300 -s 1000 <ll_addr>`
2. Record the packet loss and timings, it should be less then 10%
3. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #04 - ICMPv6 echo with iotlab-m3/samr21-xpro 15 minutes
============================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.

1. Ping from the src to the dest `ping -c 10000 -i 100 -s 100 <ll_addr>`
2. Record the packet loss and timings, it should be less then 10%
3. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #05 (Experimental) - ICMPv6 multicast echo with samr21-xpro/remote
=======================================================================
### Description

ICMPv6 echo request/reply exchange between a `samr21-xpro` a `remote-revb`

1. Set the channel on the both dest and src to 17 `ifconfig 6 set chan 17`
2. Ping from the src to the dest `ping -c 1000 -i 100 -s 50 ff02::1`
3. Record the packet loss and timings, it should be less then 10%
4. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #06 (Experimental) - ICMPv6 link-local echo with samr21-xpro/remote
========================================================================
### Description

ICMPv6 echo request/reply exchange between a `samr21-xpro` a `remote-revb`

1. Ping from the src to the dest `ping -c 1000 -i 100 -s 100 <ll_addr>`
2. Record the packet loss and timings, it should be less then 10%
3. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #07 (Experimental) - ICMPv6 multicast echo with samr21-xpro/zero + xbee
============================================================================
### Description

ICMPv6 echo request/reply exchange between a `samr21-xpro` a `arduino-zero`

1. Flash the `arduino-zero` with the
`USEMODULE=xbee BOARD=arduino-zero make flash` command
2. Set the channel on the both dest and src to 17 `ifconfig 6 set chan 17`
3. Ping from the src to the dest `ping -c 1000 -i 150 -s 50 ff02::1`
4. Record the packet loss and timings, it should be less then 10%
5. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #08 (Experimental) - ICMPv6 echo with samr21-xpro/zero + xbee
==================================================================
### Description

ICMPv6 echo request/reply exchange between a `samr21-xpro` a `arduino-zero`

1. Flash the `arduino-zero` with the
`USEMODULE=xbee BOARD=arduino-zero make flash` command
2. Ping from the src to the dest `ping -c 1000 -i 350 -s 100 <ll_addr>`
3. Record the packet loss and timings, it should be less then 10%
4. check the packet buffer with `pktbuf`

### Result

<10% packets lost on the pinging node.

Task #09 - ICMPv6 stress test on iotlab-m3
==========================================
### Description

Rapid ICMPv6 echo request/reply exchange from two iotlab-m3 nodes simultaneously
to one iotlab-m3.
1. Ping from many srcs to the dest `ping -c 1000 -i 200 -s 1232 <ll_addr>`
2. check the packet buffer with `pktbuf`
3. As long as there are no crashes and the `pktbuf` clears after some time it
is OK.

Task #10 (Exprimental) - ICMPv6 echo with large payload (IPv6 fragmentation)
============================================================================
### Description

ICMPv6 echo request/reply exchange between two nodes (make sure module
`gnrc_ipv6_ext_frag` is included and the packet buffer is large enough to handle
both the fragmented and reassembled requests/replies).
1. Compile with `CFLAGS+=GNRC_PKTBUF_SIZE=8192` and
   `USEMODULE += gnrc_ipv6_ext_frag`.
2. Ping from the src to the dest `ping -c 200 -i 600 -s 2048 <ll_addr>`
3. Record the packet loss and timings, it should be less then 10%
4. check the packet buffer with `pktbuf`
