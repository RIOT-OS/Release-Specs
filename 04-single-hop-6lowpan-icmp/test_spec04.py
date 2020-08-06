import time

import pytest

from riotctrl_shell.gnrc import GNRCICMPv6Echo, GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig

from testutils.asyncio import wait_for_futures
from testutils.shell import ping6, pktbuf, lladdr


APP = 'examples/gnrc_networking'
TASK10_APP = 'tests/gnrc_udp'
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCPktbufStats):
    pass


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr,
                count=1000, interval=20, packet_size=0)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1",
                count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr,
                count=500, interval=300, packet_size=1024)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task04(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    # enforce reconnect to pinged's terminal as connection to it in the IoT-LAB
    # sometimes get's lost silently in the CI after the 15 min of pinging
    # see https://github.com/RIOT-OS/Release-Specs/issues/189
    pinged.stop_term()
    res = ping6(pinger, pinged_addr,
                count=10000, interval=100, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    pinged.start_term()
    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'remote-revb'])],
                         indirect=['nodes'])
def test_task05(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )
    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1",
                count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'remote-revb'])],
                         indirect=['nodes'])
def test_task06(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )
    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr,
                count=1000, interval=100, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'arduino-zero'])],
                         indirect=['nodes'])
def test_task07(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd", "xbee"]),
    )

    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1",
                count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'arduino-zero'])],
                         indirect=['nodes'])
def test_task08(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd", "xbee"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr,
                count=1000, interval=350, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3',
                                        'iotlab-m3'])],
                         indirect=['nodes'])
def test_task09(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(2, APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged = nodes[0]
    pingers = nodes[1:]

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    for pinger in pingers:
        pinger_netif, _ = lladdr(pinger.ifconfig_list())
        pinger.ifconfig_set(pinger_netif, "channel", 26)

    futures = []
    for pinger in nodes[1:]:
        out = pinger.ping6(pinged_addr,
                           count=200, interval=0, packet_size=1232,
                           async_=True)
        futures.append(out)
    wait_for_futures(futures)

    time.sleep(60)
    for node in nodes:
        # add print to know which node's packet buffer is not empty on error
        print("check pktbuf on", node.riotctrl.env.get("PORT"))
        assert pktbuf(node).is_empty()


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task10(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, TASK10_APP, Shell, modules=["gnrc_pktbuf_cmd"]),
        riot_ctrl(1, TASK10_APP, Shell, modules=["gnrc_pktbuf_cmd"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr,
                count=200, interval=600, packet_size=2048)
    if 10 < res['stats']['packet_loss'] <= 100:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/issues/142#issuecomment-561677974"    # noqa: E501
        )
    assert res['stats']['packet_loss'] < 10

    time.sleep(60)
    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()
