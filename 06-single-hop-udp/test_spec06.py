import pytest
from riotctrl_shell.gnrc import GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig
from testutils.native import bridged
from testutils.shell import GNRCUDP, check_pktbuf, lladdr

APP = 'tests/net/gnrc_udp'
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCPktbufStats, GNRCUDP):
    pass


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task01(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell),
        riot_ctrl(1, APP, Shell),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(1337)

        client.udp_client_send(
            server_addr, 1337, count=1000, delay_ms=1000, payload=1024
        )
        packet_loss = server.udp_server_check_output(count=1000, delay_ms=1000)
        assert packet_loss < 5
        server.udp_server_stop()

    check_pktbuf(*nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task02(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell),
        riot_ctrl(1, APP, Shell),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(61616)

        client.udp_client_send(
            server_addr, 61616, count=1000, delay_ms=1000, payload=1024
        )
        packet_loss = server.udp_server_check_output(count=1000, delay_ms=1000)
        assert packet_loss < 5
        server.udp_server_stop()

    check_pktbuf(*nodes)


@pytest.mark.skipif(not bridged(["tap0"]), reason="tap0 not bridged")
@pytest.mark.parametrize('nodes', [pytest.param(['native'])], indirect=['nodes'])
def test_task03(riot_ctrl):
    node = riot_ctrl(0, APP, Shell, port="tap0")
    node.udp_client_send("fe80::db:b7ec", 1337, count=1000, delay_ms=0, payload=8)
    check_pktbuf(node)


@pytest.mark.iotlab_creds
@pytest.mark.parametrize('nodes', [pytest.param(['iotlab-m3'])], indirect=['nodes'])
def test_task04(riot_ctrl):
    node = riot_ctrl(0, APP, Shell)
    node.udp_client_send("fe80::db:b7ec", 1337, count=1000, delay_ms=0, payload=8)
    check_pktbuf(node)

@pytest.mark.skipif(not bridged(["tap0"]), reason="tap0 not bridged")
@pytest.mark.parametrize('nodes', [pytest.param(['native64'])], indirect=['nodes'])
def test_task05(riot_ctrl):
    node = riot_ctrl(0, APP, Shell, port="tap0")
    node.udp_client_send("fe80::db:b7ec", 1337, count=1000, delay_ms=0, payload=8)
    check_pktbuf(node)

@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native', 'native'])], indirect=['nodes']
)
def test_task06(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, port="tap0"),
        riot_ctrl(1, APP, Shell, port="tap1"),
    )

    for client, server in zip(nodes, reversed(nodes)):
        _, server_addr = lladdr(server.ifconfig_list())
        assert server_addr.startswith("fe80::")

        server.udp_server_start(1337)

        client.udp_client_send(server_addr, 1337, count=100, delay_ms=100, payload=0)
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        assert packet_loss <= 10
        server.udp_server_stop()

    check_pktbuf(*nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task07(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell),
        riot_ctrl(1, APP, Shell),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(1337)

        client.udp_client_send(server_addr, 1337, count=100, delay_ms=100, payload=0)
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        assert packet_loss <= 10
        server.udp_server_stop()

    check_pktbuf(*nodes)

@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native64', 'native64'])], indirect=['nodes']
)
def test_task08(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, port="tap0"),
        riot_ctrl(1, APP, Shell, port="tap1"),
    )

    for client, server in zip(nodes, reversed(nodes)):
        _, server_addr = lladdr(server.ifconfig_list())
        assert server_addr.startswith("fe80::")

        server.udp_server_start(1337)

        client.udp_client_send(server_addr, 1337, count=100, delay_ms=100, payload=0)
        packet_loss = server.udp_server_check_output(count=100, delay_ms=100)
        assert packet_loss <= 10
        server.udp_server_stop()

    check_pktbuf(*nodes)
