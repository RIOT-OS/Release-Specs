#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Martine Lenders <mail@martine-lenders.eu>
#
# Distributed under terms of the MIT license.

import pytest

import riotctrl_shell.gnrc
import riotctrl_shell.netif
import riotctrl_shell.tests.common
from riotctrl_shell.tests.common import init_ctrl

import testutils.shell

STRING_PKTBUF_EMPTY = """
packet buffer: first byte: 0x5660dce0, last byte: 0x5660fce0 (size: 8192)
  position of last byte used: 1792
~ unused: 0x5660dce0 (next: (nil), size: 8192) ~
"""

STRING_PKTBUF_NOT_EMPTY = """
packet buffer: first byte: 0x5660dce0, last byte: 0x5660fce0 (size: 8192)
  position of last byte used: 1792
~ unused: 0x5660de00 (next: (nil), size: 7904) ~
"""


def test_ping6():
    ctrl = init_ctrl(output="""
12 bytes from ::1: icmp_seq=0 ttl=64
12 bytes from ::1: icmp_seq=1 ttl=64
12 bytes from ::1: icmp_seq=2 ttl=64

--- ::1 PING statistics ---
3 packets transmitted, 3 packets received, 0% packet loss""")
    shell = riotctrl_shell.gnrc.GNRCICMPv6Echo(ctrl)
    ping_res = testutils.shell.ping6(shell, "ff02::1", 3, 4, 1000)
    assert ping_res
    assert len(ping_res["replies"]) == 3
    assert ping_res["stats"]["packet_loss"] == 0


def test_pktbuf_empty():
    ctrl = init_ctrl(output=STRING_PKTBUF_EMPTY)
    shell = riotctrl_shell.gnrc.GNRCPktbufStats(ctrl)
    pktbuf_res = testutils.shell.pktbuf(shell)
    assert pktbuf_res
    assert pktbuf_res.is_empty()


def test_pktbuf_not_empty():
    ctrl = init_ctrl(output=STRING_PKTBUF_NOT_EMPTY)
    shell = riotctrl_shell.gnrc.GNRCPktbufStats(ctrl)
    pktbuf_res = testutils.shell.pktbuf(shell)
    assert pktbuf_res
    assert not pktbuf_res.is_empty()


def test_lladdr():
    netif, lladdr = testutils.shell.lladdr("""
Iface  6  HWaddr: 6A:2E:4F:3D:DF:CB
          L2-PDU:1500  MTU:1500  HL:64  RTR
          RTR_ADV
          Source address length: 6
          Link type: wired
          inet6 addr: fe80::682e:4fff:fe3d:dfcb  scope: link  VAL
          inet6 group: ff02::2
          inet6 group: ff02::1
          inet6 group: ff02::1:ff3d:dfcb
            """)
    assert netif == "6"
    assert lladdr == "fe80::682e:4fff:fe3d:dfcb"


def test_lladdr_no_lladdr():
    with pytest.raises(KeyError):
        testutils.shell.lladdr("""
Iface  4  HWaddr: 6A:2E:4F:3D:DF:CB
          L2-PDU:1500  Source address length: 6
            """)


def test_global_addr():
    netif, global_addr = testutils.shell.global_addr("""
Iface  6  HWaddr: 6A:2E:4F:3D:DF:CB
          L2-PDU:1500  MTU:1500  HL:64  RTR
          RTR_ADV
          Source address length: 6
          Link type: wired
          inet6 addr: fe80::682e:4fff:fe3d:dfcb  scope: link  VAL
          inet6 addr: 2001:db8::682e:4fff:fe3d:dfcb  scope: global  VAL
          inet6 group: ff02::2
          inet6 group: ff02::1
          inet6 group: ff02::1:ff3d:dfcb
            """)
    assert netif == "6"
    assert global_addr == "2001:db8::682e:4fff:fe3d:dfcb"


def test_global_addr_no_global_addr():
    with pytest.raises(IndexError):
        testutils.shell.global_addr("""
Iface  6  HWaddr: 6A:2E:4F:3D:DF:CB
          L2-PDU:1500  MTU:1500  HL:64  RTR
          RTR_ADV
          Source address length: 6
          Link type: wired
          inet6 addr: fe80::682e:4fff:fe3d:dfcb  scope: link  VAL
          inet6 group: ff02::2
          inet6 group: ff02::1
          inet6 group: ff02::1:ff3d:dfcb
            """)


def test_check_pktbuf_empty(monkeypatch):
    requested_secs = []
    nodes = []

    def sleep(secs):
        requested_secs.append(secs)

    ctrl = init_ctrl(output=STRING_PKTBUF_EMPTY)
    nodes.append(riotctrl_shell.gnrc.GNRCPktbufStats(ctrl))

    ctrl = init_ctrl(output=STRING_PKTBUF_NOT_EMPTY)
    nodes.append(riotctrl_shell.gnrc.GNRCPktbufStats(ctrl))

    monkeypatch.setattr("time.sleep", sleep)
    testutils.shell.check_pktbuf(nodes[0], wait=10)

    assert len(requested_secs) == 1
    assert requested_secs.pop() == 10

    testutils.shell.check_pktbuf(nodes[0], nodes[0], wait=0)

    assert len(requested_secs) == 0

    with pytest.raises(AssertionError):
        testutils.shell.check_pktbuf(*nodes)


def test_ifconfig():
    ctrl = init_ctrl(output="""
ifconfig
Iface  3  HWaddr: 26:01:24:C0  Frequency: 869524963Hz  BW: 125kHz  SF: 12  CR: 4/5  Link: up
           TX-Power: 14dBm  State: SLEEP  Demod margin.: 0  Num gateways.: 0
          IQ_INVERT
          RX_SINGLE  OTAA  L2-PDU:2559
          """)  # noqa: E501
    shell = riotctrl_shell.netif.Ifconfig(ctrl)
    res = testutils.shell.ifconfig(shell)
    assert len(res) == 1
    assert '3' in res


def test_lorawan_netif_None():
    ctrl = init_ctrl(output="""
ifconfig
Iface  7  HWaddr: 76:F5:98:9F:40:22
          L2-PDU:1500  MTU:1500  HL:64  RTR
          Source address length: 6
          Link type: wired
          inet6 addr: fe80::74f5:98ff:fe9f:4022  scope: link  VAL
          inet6 addr: fe80::2  scope: link  VAL
          inet6 group: ff02::2
          inet6 group: ff02::1
          inet6 group: ff02::1:ff9f:4022
          inet6 group: ff02::1:ff00:2
          """)
    shell = riotctrl_shell.netif.Ifconfig(ctrl)
    res = testutils.shell.lorawan_netif(shell)
    assert res is None


def test_lorawan_netif_no_lorawan():
    ctrl = init_ctrl(output="""
ifconfig
Iface  3  HWaddr: 26:01:24:C0  Frequency: 869524963Hz  BW: 125kHz  SF: 12  CR: 4/5  Link: up
           TX-Power: 14dBm  State: SLEEP  Demod margin.: 0  Num gateways.: 0
          IQ_INVERT
          RX_SINGLE  OTAA  L2-PDU:2559
          """)  # noqa: E501
    shell = riotctrl_shell.netif.Ifconfig(ctrl)
    res = testutils.shell.lorawan_netif(shell)
    assert res == 3


def test_gnrc_lorawan_send_success():
    ctrl = init_ctrl(output="""
txtsnd 3 "Hello RIOT!" 2
Successfully sent packet
""")
    shell = testutils.shell.GNRCLoRaWANSend(ctrl)
    res = shell.txtsnd(3, "Hello RIOT!")
    assert res is False


def test_gnrc_lorawan_send_success_downlink():
    ctrl = init_ctrl(output="""
txtsnd 3 "Hello RIOT!" 2
PKTDUMP: data received:
~~ SNIP  0 - size:   4 byte, type: NETTYPE_LORAWAN (1)
00000000  AA  AA  AA  AA
~~ PKT    -  1 snips, total size:   4 byte
Successfully sent packet
""")
    with ctrl.run_term():
        shell = testutils.shell.GNRCLoRaWANSend(ctrl)
        shell.riotctrl.term.expect_res = 1
        res = shell.txtsnd(3, "Hello RIOT!")
        assert res is True
