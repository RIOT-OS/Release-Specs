import time

import pytest

from riotctrl_shell.gnrc import GNRCICMPv6Echo, GNRCIPv6NIB, GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig

from testutils.shell import lladdr, global_addr, ping6, GNRCUDP, PARSERS, check_pktbuf


APP = 'tests/net/gnrc_udp'
TO_ADDR = "affe::1"  # address for the first statically routed node
FROM_ADDR = "beef::1"  # address for the last statically routed node
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCIPv6NIB, GNRCPktbufStats, GNRCUDP):
    pass


@pytest.fixture
def statically_routed_nodes(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell),
        riot_ctrl(1, APP, Shell),
        riot_ctrl(2, APP, Shell),
        riot_ctrl(3, APP, Shell),
    )
    lladdrs = [
        dict(zip(("netif", "lladdr"), lladdr(node.ifconfig_list()))) for node in nodes
    ]
    from_addr = FROM_ADDR + "/64"
    to_addr = TO_ADDR + "/64"
    nodes[0].ifconfig_add(lladdrs[0]["netif"], from_addr)
    nodes[-1].ifconfig_add(lladdrs[-1]["netif"], to_addr)
    for i, node in enumerate(nodes):
        if i < (len(nodes) - 1):
            # set to-route
            node.nib_route_add(lladdrs[i]["netif"], to_addr, lladdrs[i + 1]["lladdr"])
        if i > 0:
            # set from-route
            node.nib_route_add(lladdrs[i]["netif"], from_addr, lladdrs[i - 1]["lladdr"])
    return nodes


@pytest.fixture
def netif_parser():
    return PARSERS["ifconfig"]


# pylint: disable=W0621
def _get_nodes_netifs(nodes, netif_parser):
    nodes_netifs = []
    for node in nodes:
        netifs = netif_parser.parse(node.ifconfig_list())
        key = next(iter(netifs))
        nodes_netifs.append(
            {
                "netif": key,
                "hwaddr": netifs[key]["long_hwaddr"],
                "lladdr": [
                    addr["addr"]
                    for addr in netifs[key]["ipv6_addrs"]
                    if addr["scope"] == "link"
                ][0],
            }
        )
    return nodes_netifs


def _l2filter_nodes(nodes, nodes_netifs):
    for i, node in enumerate(nodes):
        if i < (len(nodes) - 1):
            # set to-route
            node.ifconfig_l2filter_add(
                nodes_netifs[i]["netif"], nodes_netifs[i + 1]["hwaddr"]
            )
        if i > 0:
            # set from-route
            node.ifconfig_l2filter_add(
                nodes_netifs[i]["netif"], nodes_netifs[i - 1]["hwaddr"]
            )


def _init_rpl_dodag(nodes, nodes_netifs):
    dodag_id = nodes_netifs[0]["lladdr"].replace("fe80::", "2001:db8::")
    nodes[0].ifconfig_add(nodes_netifs[0]["netif"], dodag_id + "/64")
    # TODO provide rpl ShellInteraction in `riotctrl_shell` upstream
    res = nodes[0].cmd(f"rpl init {nodes_netifs[0]['netif']}")
    if "success" not in res:
        raise RuntimeError(res)
    res = nodes[0].cmd(f"rpl root 0 {dodag_id}")
    if "success" not in res:
        raise RuntimeError(res)
    for i, node in enumerate(nodes[1:], 1):
        res = node.cmd(f"rpl init {nodes_netifs[i]['netif']}")
        if "success" not in res:
            raise RuntimeError(res)
    nodes_configured = [False]
    while not all(nodes_configured):
        time.sleep(10)
        nodes_configured = [False for node in nodes[1:]]
        for i, node in enumerate(nodes[1:]):
            res = node.cmd("rpl show")
            nodes_configured[i] = dodag_id in res


@pytest.fixture
# pylint: disable=W0621
def rpl_nodes(riot_ctrl, netif_parser):
    nodes = (
        riot_ctrl(0, APP, Shell, modules="l2filter_whitelist"),
        riot_ctrl(1, APP, Shell, modules="l2filter_whitelist"),
        riot_ctrl(2, APP, Shell, modules="l2filter_whitelist"),
        riot_ctrl(3, APP, Shell, modules="l2filter_whitelist"),
    )
    nodes_netifs = _get_nodes_netifs(nodes, netif_parser)
    _l2filter_nodes(nodes, nodes_netifs)
    _init_rpl_dodag(nodes, nodes_netifs)
    return nodes


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to statically_routed_nodes for riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3', 'iotlab-m3'])],
    indirect=['nodes'],
)
def test_task01(statically_routed_nodes):
    pinger = statically_routed_nodes[0]

    res = ping6(pinger, TO_ADDR, count=100, packet_size=50, interval=100)
    assert res["stats"]["packet_loss"] < 20
    check_pktbuf(*statically_routed_nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to statically_routed_nodes for riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3', 'iotlab-m3'])],
    indirect=['nodes'],
)
def test_task02(statically_routed_nodes):
    nodes = statically_routed_nodes
    for client, server, server_addr in [
        (nodes[0], nodes[-1], TO_ADDR),
        (nodes[-1], nodes[0], FROM_ADDR),
    ]:
        server.udp_server_start(1337)

        client.udp_client_send(server_addr, 1337, count=100, delay_ms=100, payload=50)
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        assert packet_loss < 10
        server.udp_server_stop()
    check_pktbuf(*statically_routed_nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to rpl_nodes for riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3', 'iotlab-m3'])],
    indirect=['nodes'],
)
def test_task03(rpl_nodes):
    pinger = rpl_nodes[-1]

    _, root_addr = global_addr(rpl_nodes[0].ifconfig_list())
    res = ping6(pinger, root_addr, count=100, packet_size=50, interval=100)
    assert res["stats"]["packet_loss"] < 20
    check_pktbuf(*rpl_nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to rpl_nodes for riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3', 'iotlab-m3'])],
    indirect=['nodes'],
)
def test_task04(rpl_nodes):
    nodes = rpl_nodes
    for client, server in [(nodes[0], nodes[-1]), (nodes[-1], nodes[0])]:
        server.udp_server_start(1337)
        _, server_addr = global_addr(server.ifconfig_list())

        client.udp_client_send(server_addr, 1337, count=100, delay_ms=100, payload=50)
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        assert packet_loss < 10
        server.udp_server_stop()
    check_pktbuf(*rpl_nodes)


@pytest.mark.iotlab_creds
# nodes passed to rpl_nodes for riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3', 'iotlab-m3'])],
    indirect=['nodes'],
)
def test_task05(rpl_nodes):
    nodes = rpl_nodes
    for client, server in [(nodes[0], nodes[-1]), (nodes[-1], nodes[0])]:
        server.udp_server_start(1337)
        _, server_addr = global_addr(server.ifconfig_list())

        client.udp_client_send(
            server_addr, 1337, count=100, delay_ms=1000, payload=2048
        )
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        if packet_loss >= 10:
            pytest.xfail(
                f"packet_loss {packet_loss} >= 10. This is an experimental "
                "task, see also "
                # pylint: disable=C0301
                "https://github.com/RIOT-OS/Release-Specs/issues/142#issuecomment-561677974"  # noqa: E501
            )
        assert packet_loss < 10
        server.udp_server_stop()
    check_pktbuf(*rpl_nodes)
