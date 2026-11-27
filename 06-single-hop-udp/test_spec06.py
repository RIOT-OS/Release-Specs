import pytest

from riotctrl_shell.gnrc import GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig
from riotctrl_shell.udp import UDPClientSendGenerated, UDPServer

from testutils.native import bridged
from testutils.shell import lladdr, check_pktbuf

APP = 'examples/networking/gnrc/networking'
CFLAGS = "-DCONFIG_GNRC_PKTBUF_SIZE=8192"
USEMODULE = [
    "gnrc_ipv6_ext_frag",
    "shell_cmd_udp_send_generated",
    "shell_cmd_gnrc_pktbuf",
]
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCPktbufStats, UDPClientSendGenerated, UDPServer):
    pass


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task01(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
        riot_ctrl(1, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(1337, summarize=True)

        client.udp_client_send(
            server_addr, 1337, count=1000, delay_us=1_000_000, payload=1024
        )
        packet_loss = server.udp_server_check_output(count=1000, delay_us=1_000_000)
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
        riot_ctrl(0, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
        riot_ctrl(1, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(61616, summarize=True)

        client.udp_client_send(
            server_addr, 61616, count=1000, delay_us=1_000_000, payload=1024
        )
        packet_loss = server.udp_server_check_output(count=1000, delay_us=1_000_000)
        assert packet_loss < 5
        server.udp_server_stop()

    check_pktbuf(*nodes)


@pytest.mark.skipif(not bridged(["tap0"]), reason="tap0 not bridged")
@pytest.mark.parametrize('nodes', [pytest.param(['native'])], indirect=['nodes'])
def test_task03(riot_ctrl):
    node = riot_ctrl(0, APP, Shell, port="tap0", modules=USEMODULE, cflags=CFLAGS)
    node.udp_client_send(
        "fe80::db:b7ec", 1337, count=1000, delay_us=1_000_000, payload=8
    )
    check_pktbuf(node)


@pytest.mark.iotlab_creds
@pytest.mark.parametrize('nodes', [pytest.param(['iotlab-m3'])], indirect=['nodes'])
def test_task04(riot_ctrl):
    node = riot_ctrl(0, APP, Shell, modules=USEMODULE, cflags=CFLAGS)
    node.udp_client_send("fe80::db:b7ec", 1337, count=1000, delay_us=0, payload=8)
    check_pktbuf(node)


@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native', 'native'])], indirect=['nodes']
)
def test_task05(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, port="tap0", modules=USEMODULE, cflags=CFLAGS),
        riot_ctrl(1, APP, Shell, port="tap1", modules=USEMODULE, cflags=CFLAGS),
    )

    for client, server in zip(nodes, reversed(nodes)):
        _, server_addr = lladdr(server.ifconfig_list())
        assert server_addr.startswith("fe80::")

        server.udp_server_start(1337, summarize=True)

        client.udp_client_send(
            server_addr, 1337, count=100, delay_us=100_000, payload=0
        )
        packet_loss = server.udp_server_check_output(count=100, delay_us=100_000)
        assert packet_loss <= 10
        server.udp_server_stop()

    check_pktbuf(*nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task06(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
        riot_ctrl(1, APP, Shell, modules=USEMODULE, cflags=CFLAGS),
    )

    for client, server in zip(nodes, reversed(nodes)):
        server_netif, server_addr = lladdr(server.ifconfig_list())
        server.ifconfig_set(server_netif, "channel", 26)
        assert server_addr.startswith("fe80::")
        client_netif, _ = lladdr(client.ifconfig_list())
        client.ifconfig_set(client_netif, "channel", 26)

        server.udp_server_start(1337, summarize=True)

        client.udp_client_send(
            server_addr, 1337, count=100, delay_us=100_000, payload=0
        )
        packet_loss = server.udp_server_check_output(count=100, delay_us=100_000)
        assert packet_loss <= 10
        server.udp_server_stop()

    check_pktbuf(*nodes)
