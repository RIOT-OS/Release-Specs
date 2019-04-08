Summary
=======

This file gives an indication of the automation and coverage improvements
that can be made in the testing.

Test 01-ci
==========

| Task no | Description                                | Automated? | Ease of automation |
|---------|--------------------------------------------|------------|--------------------|
| 1       | Compile all applications for all boards    | Yes        | N/A                |
| 2       | Run all unit tests in native               | Yes        | N/A                |
| 3       | Run all unit tests separately in native    | Yes        | N/A                |
| 4       | Run all unit tests on an IoT-Lab M3 node   | Yes        | N/A                |

Currently, this is not being run on the reference Docker platform. There is a
significant amount of work required to enable these tests to be run in Docker
but this is also desirable.

Test 02-tests
=============

| Task no | Description                                | Automated? | Ease of automation |
|---------|--------------------------------------------|------------|--------------------|
| 1       | Compile and run tests on native            | Partly     | Easy               |
| 2       | Compile and run tests on IoT-Lab M3        | Partly     | Easy               |
| 3       | Compile and run tests on SAMR21-xpro       | Partly     | Easy               |

The tests to run are currently specified manually. Additionally, there are
tests which could be run automatically which cannot because of their
implementation. Further automation would involve automatic discovery of the
appropriate tests and expansion of the tests that can be performed.

Test 03-single-hop-ipv6-icmp
============================

| Task no | Description                                  | Automated? | Ease of automation |
|---------|----------------------------------------------|------------|--------------------|
| 1       | ICMPv6 multicast echo on native              | No         | Easy               |
| 2       | ICMPv6 link local echo on native - rapid     | No         | Easy               |
| 3       | ICMPv6 link local echo on native - extended  | No         | Easy               |
| 4       | ICMPv6 stress test on native                 | No         | Easy               |
| 5       | ICMPv6 neighbour cache stress test on native | No         | Easy               |

Test 04-single-hop-6lowpan-icmp
===============================

| Task no | Description                                                       | Automated? | Ease of automation |
|---------|-------------------------------------------------------------------|------------|--------------------|
| 1       | ICMPv6 link local echo on IoT-Lab M3                              | In PR 79   | Easy               |
| 2       | ICMPv6 multicast echo between SAMR21-xpro and IoT-Lab M3          | In PR 79   | Easy               |
| 3       | ICMPv6 echo with large payload                                    | In PR 79   | Easy               |
| 4       | ICMPv6 echo between SAMR21-xpro and IoT-Lab M3 - 15 minutes       | In PR 79   | Easy               |
| 5       | ICMPv6 multicast echo between SAMR21-xpro and Zolertia Remote     | No         | Easy               |
| 6       | ICMPv6 link-local echo between SAMR21-xpro and Zolertia Remote    | No         | Easy               |
| 7       | ICMPv6 multicast echo between SAMR21-xpro and Arduino Zero + XBee | In PR 79   | Easy               |
| 8       | ICMPv6 echo between SAMR21-xpro and Arduino Zero + XBee           | No         | Easy               |
| 9       | ICMPv6 stress test between several IoT-Lab M3 nodes               | No         | Easy               |

Test 05-single-hop-route
========================

| Task no | Description                                                | Automated? | Ease of automation |
|---------|------------------------------------------------------------|------------|--------------------|
| 1       | ICMPv6 echo unicast addresess on native (default route)    | No         | Easy               |
| 2       | ICMPv6 echo unicast addresess on iotlab-m3 (default route) | No         | Easy               |
| 3       | ICMPv6 echo unicast addresess on native (specific route)   | No         | Easy               |
| 4       | ICMPv6 echo unicast addresess on iotlab-m3 (static route)  | No         | Easy               |

Test 06-single-hop-udp
======================

| Task no | Description                              | Automated? | Ease of automation |
|---------|------------------------------------------|------------|--------------------|
| 1       | UDP on iotlab-m3                         | No         | Hard               |
| 2       | UDP on iotlab-m3 (UDP port compression)  | No         | Hard               |
| 3       | UDP on native (non-existent neighbor)    | No         | Easy               |
| 4       | UDP on iotlab-m3 (non-existent neighbor) | No         | Hard               |

Test 07-multi-hop
=================

| Task no | Description                                             | Automated? | Ease of automation |
|---------|---------------------------------------------------------|------------|--------------------|
| 1       | ICMPv6 echo on iotlab-m3 with three hops (static route) | No         | Easy               |
| 2       | UDP on iotlab-m3 with three hops (static route)         | No         | Easy               |
| 3       | ICMPv6 echo on iotlab-m3 with three hops (RPL route)    | No         | Easy               |
| 4       | UDP on iotlab-m3 with three hops (RPL route)            | No         | Easy               |

Test 08-interop
===============

| Task no | Description                                                                       | Automated? | Ease of automation |
|---------|-----------------------------------------------------------------------------------|------------|--------------------|
| 1       | ICMPv6 echo between native and Linux                                              | No         | Easy               |
| 2       | ICMPv6 echo between iotlab-m3 and Linux with 6LowPAN                              | No         | Hard               |
| 3       | ICMPv6 echo between iotlab-m3 and Contiki                                         | No         | Hard               |
| 4       | ICMPv6 echo between iotlab-m3 and Internet host through Linux with 6LowPAN        | No         | Hard               |
| 5       | ICMPv6 echo between iotlab-m3 and Internet host through RIOT border router        | No         | Hard               |
| 6       | UDP between iotlab-m3 and Internet host through RIOT border router                | No         | Hard               |
| 7       | UDP between iotlab-m3 and Internet host through RIOT border router (200b payload) | No         | Hard               |
| 8       | UDP between GNRC and lwIP on iotlab-m3                                            | No         | Hard               |
| 9       | UDP between GNRC and emb6 on iotlab-m3                                            | No         | Hard               |
| 10      | UDP between lwIP and emb6 on iotlab-m3                                            | No         | Hard               |

Test 09-CoAP
============

| Task no | Description                           | Automated? | Ease of automation |
|---------|---------------------------------------|------------|--------------------|
| 1       | CORD Endpoint                         | No         | Easy               |
| 2       | Confirmable retries                   | No         | Easy               |
| 3       | Block1                                | No         | Easy               |
| 4       | Block2                                | No         | Easy               |
| 5       | Observe registration and notification | No         | Easy               |


Test 10-icmpv6-error
====================

| Task no | Description                                                         | Automated? | Ease of automation |
|---------|---------------------------------------------------------------------|------------|--------------------|
| 1       | Destination unreachable - no route to destination                   | No         | Easy               |
| 2       | Destination unreachable - Beyond scope of source address            | No         | Easy               |
| 3       | Destination unreachable - address unreachable (target node address) | No         | Easy               |
| 4       | Destination unreachable - address unreachable (neighbor cache miss) | No         | Easy               |
| 5       | Destination unreachable - port unreachable                          | No         | Easy               |
| 6       | Destination unreachable - port unreachable (large payload)          | No         | Easy               |
| 7       | Packet too big                                                      | No         | Easy               |
| 8       | Time exceeded - hop limit exceeded in transit                       | No         | Easy               |
| 9       | Parameter problem - erroneous header field encountered              | No         | Easy               |
| 10      | IPv6-in-IPv6 encapsulation                                          | No         | Easy               |

Test 11-lorawan
===============

| Task no | Description                           | Automated? | Ease of automation |
|---------|---------------------------------------|------------|--------------------|
| 1       | LoRaWAN example                       | No         | Hard               |
| 2       | OTAA join procedure                   | No         | Hard               |
| 3       | ABP join procedure                    | No         | Hard               |
| 4       | LoRaWAN device parameters persistence | No         | Hard               |

Test 99-compile-and-test-one-board
==================================

| Task no | Description                           | Automated? | Ease of automation |
|---------|---------------------------------------|------------|--------------------|
| 1       | Run test 02 on additional hardware    | Yes        | N/A                |
