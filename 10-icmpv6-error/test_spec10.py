import time

import pytest
# pylint: disable=E0611
from scapy.all import raw, sendp, srp1, Ether, IPv6, UDP, AsyncSniffer, \
                      ICMPv6EchoReply, ICMPv6EchoRequest, \
                      ICMPv6DestUnreach, ICMPv6PacketTooBig, \
                      ICMPv6TimeExceeded, ICMPv6ParamProblem, \
                      IPerror6, UDPerror

from riotctrl_shell.gnrc import GNRCIPv6NIB
from riotctrl_shell.netif import Ifconfig, IfconfigListParser

from testutils.native import bridge, get_link_local, interface_exists, \
                             ip_addr_add, ip_addr_del, \
                             ip_route_add, ip_route_del


APP = 'examples/gnrc_networking'
TAP = 'tap0'
NETIF_PARSER = IfconfigListParser()


pytestmark = pytest.mark.rc_only()


class Shell(GNRCIPv6NIB, Ifconfig):
    pass


# pylint: disable=W0613
def setup_function(function):
    host_netif = bridge(TAP)
    ip_addr_del(host_netif, "beef::1/64")
    ip_route_del(host_netif, "affe::1/64")


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    ip_addr_add(host_netif, "beef::1/64")
    ip_route_add(host_netif, "affe::/64", node_lladdr)
    node.nib_route_add(node_netif, "beef::/64", host_lladdr)

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src="beef::1", dst="affe::1") /
               UDP(dport=48879),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 0
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    node_hwaddr = node_netifs[node_netif]["hwaddr"]

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src=host_lladdr, dst="affe::1") /
               UDP(dport=48879),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 2
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    node_hwaddr = node_netifs[node_netif]["hwaddr"]

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src=host_lladdr, dst="fe80::1") /
               UDP(dport=48879),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 3
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task04(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    ip_addr_add(host_netif, "beef::1/64")
    ip_route_add(host_netif, "affe::/64", node_lladdr)
    node.nib_route_add(node_netif, "beef::/64", host_lladdr)
    node.nib_route_add(node_netif, "affe::/64", "fe80::ab25:f123")

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src="beef::1", dst="affe::1") /
               UDP(dport=48879),
               iface=host_netif,
               timeout=10,  # needs to wait for address resolution
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 3
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task05(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src=host_lladdr, dst=node_lladdr) /
               UDP(dport=48879),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 4
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task06(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src=host_lladdr, dst=node_lladdr) /
               UDP(dport=48879) / ("x" * 1452),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6DestUnreach in pkt
    assert pkt[ICMPv6DestUnreach].code == 4
    assert pkt[IPv6].src == node_lladdr
    assert UDPerror in pkt
    assert len(pkt[UDPerror].payload) <= 1404   # payload was truncated


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task07(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell,
                     cflags="-DCONFIG_GNRC_IPV6_NIB_SLAAC=1 "
                            "-DCONFIG_GNRC_IPV6_NIB_QUEUE_PKT=1",
                     termflags="-z [::]:17755", modules="socket_zep",
                     port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    time.sleep(5)
    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = [n for n in node_netifs if node_netifs[n]["mtu"] == 1500][0]
    fwd_netif = [n for n in node_netifs if node_netifs[n]["mtu"] < 1500][0]
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    ip_addr_add(host_netif, "beef::1/64")
    ip_route_add(host_netif, "affe::/64", node_lladdr)
    node.nib_route_add(node_netif, "beef::/64", host_lladdr)
    node.nib_route_add(fwd_netif, "affe::/64", "fe80::ab25:f123")

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src="beef::1", dst="affe::1") /
               UDP(dport=48879) / ("x" * 1452),
               iface=host_netif, timeout=5,
               verbose=log_nodes)
    assert ICMPv6PacketTooBig in pkt
    assert pkt[ICMPv6PacketTooBig].code == 0
    assert node_netifs[fwd_netif]["mtu"] == pkt[ICMPv6PacketTooBig].mtu == 1280
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task08(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    ip_addr_add(host_netif, "beef::1/64")
    ip_route_add(host_netif, "affe::/64", node_lladdr)
    node.nib_route_add(node_netif, "beef::/64", host_lladdr)
    node.nib_route_add(node_netif, "affe::/64", "fe80::ab25:f123")

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src="beef::1", dst="affe::1", hlim=1) /
               UDP(dport=48879),
               iface=host_netif,
               timeout=5,
               verbose=log_nodes)
    assert ICMPv6TimeExceeded in pkt
    assert pkt[ICMPv6TimeExceeded].code == 0
    assert pkt[IPv6].src == node_lladdr


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task09(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]
    ip_addr_add(host_netif, "beef::1/64")
    ip_route_add(host_netif, "affe::/64", node_lladdr)
    node.nib_route_add(node_netif, "beef::/64", host_lladdr)
    node.nib_route_add(node_netif, "affe::/64", "fe80::ab25:f123")

    pkt = srp1(Ether(dst=node_hwaddr) /
               IPv6(src="beef::1", dst="affe::1", plen=20) /
               UDP(dport=48879),
               iface=host_netif,
               timeout=5,
               verbose=log_nodes)
    assert ICMPv6ParamProblem in pkt
    assert pkt[ICMPv6ParamProblem].code == 0
    err_bytes = raw(pkt[IPerror6])
    ptr = pkt[ICMPv6ParamProblem].ptr
    # plen is a 2 byte field in network byte order (big endian)
    ptr_val = (err_bytes[ptr] << 8) | err_bytes[ptr + 1]
    assert ptr_val == 20
    assert pkt[IPv6].src == node_lladdr


def _max_encapsulations():
    """
    Calculates the maximum number of IPv6 headers that can be encapsulated
    within each other without exceeding the MTU of Ethernet.
    """
    i = 1
    ip_hdr_len = len(IPv6())
    while ((i * ip_hdr_len) + 8) < 1500:
        i += 1
    return i - 1


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only()
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task10(riot_ctrl, log_nodes):
    # pylint: disable=R0914
    node = riot_ctrl(0, APP, Shell, port=TAP)
    host_netif = bridge(TAP)
    host_lladdr = get_link_local(host_netif)

    node_netifs = NETIF_PARSER.parse(node.ifconfig_list())
    node_netif = next(iter(node_netifs))
    node_hwaddr = node_netifs[node_netif]["hwaddr"]
    node_lladdr = [addr["addr"]
                   for addr in node_netifs[node_netif]["ipv6_addrs"]
                   if addr["scope"] == "link"][0]

    ip = IPv6(src=host_lladdr, dst=node_lladdr)
    stop_id = 0xc07c
    test_id = 0xb488
    sniffer = AsyncSniffer(
        stop_filter=lambda p: ICMPv6EchoReply in p and
        p[ICMPv6EchoReply].id == stop_id,
        iface=host_netif,
    )
    sniffer.start()
    time.sleep(.1)
    max_pkts = _max_encapsulations()
    for i in range(max_pkts):
        start = time.time()
        ips = ip
        for _ in range(i):
            ips /= ip
        sendp(Ether(dst=node_hwaddr) / ips /
              ICMPv6EchoRequest(id=test_id, seq=i), iface=host_netif,
              verbose=log_nodes)
        stop = time.time()
        if (stop - start) <= 0.001:
            time.sleep(0.001 - (stop - start))
    # send stop condition for sniffer
    sendp(Ether(dst=node_hwaddr) / ip /
          ICMPv6EchoRequest(id=stop_id), iface=host_netif, verbose=log_nodes)
    sniffer.join()
    pkts = sniffer.results
    requests = [p for p in pkts if ICMPv6EchoRequest in p and
                p[ICMPv6EchoRequest].id == test_id]
    replies = [p for p in pkts if ICMPv6EchoReply in p and
               p[ICMPv6EchoReply].id == test_id]
    assert len(requests) <= max_pkts
    assert len(replies) <= max_pkts
    assert (len(replies) / max_pkts) > .96
    reply_seqs = [r[ICMPv6EchoReply].seq for r in replies]
    reply_seq_occs = [reply_seqs.count(seq) for seq in reply_seqs]
    # no sequence number occurs more than once in the replies
    assert not any(occ > 1 for occ in reply_seq_occs)
