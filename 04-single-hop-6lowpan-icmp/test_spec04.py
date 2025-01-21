import subprocess

import pytest

from riotctrl_shell.gnrc import GNRCICMPv6Echo, GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig

from testutils.asyncio import wait_for_futures
from testutils.shell import ping6, lladdr, check_pktbuf


APP = 'examples/gnrc_networking'
TASK10_APP = 'tests/net/gnrc_udp'
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCPktbufStats):
    pass


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task01(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=1000, interval=20, packet_size=0)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['samr21-xpro', 'iotlab-m3'], "saclay")], indirect=['nodes']
)
def test_task02(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
    )

    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1", count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task03(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=500, interval=300, packet_size=1024)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['samr21-xpro', 'iotlab-m3'], "saclay")], indirect=['nodes']
)
def test_task04(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
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
    res = ping6(pinger, pinged_addr, count=10000, interval=100, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    pinged.start_term()
    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes and iotlab_site passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes, iotlab_site',
    [pytest.param(['iotlab-m3', 'openmote-b'], "strasbourg")],
    indirect=['nodes', 'iotlab_site'],
)
def test_task05(riot_ctrl):
    try:
        pinger, pinged = (
            riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        )
    except subprocess.CalledProcessError:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/pull/198#issuecomment-756756109"  # noqa: E501
        )
    pinged_netif, _ = lladdr(pinged.ifconfig_list(), ignore_chan_0=True)
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list(), ignore_chan_0=True)
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1", count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes and iotlab_site passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes, iotlab_site',
    [pytest.param(['iotlab-m3', 'openmote-b'], "strasbourg")],
    indirect=['nodes', 'iotlab_site'],
)
def test_task06(riot_ctrl):
    try:
        pinger, pinged = (
            riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        )
    except subprocess.CalledProcessError:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/pull/198#issuecomment-758522278"  # noqa: E501
        )
    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list(), ignore_chan_0=True)
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list(), ignore_chan_0=True)
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=1000, interval=100, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['samr21-xpro', 'arduino-zero'], "saclay")],
    indirect=['nodes'],
)
def test_task07(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf", "xbee"]),
    )

    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1", count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.local_only
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['samr21-xpro', 'arduino-zero'], "saclay")],
    indirect=['nodes'],
)
def test_task08(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf", "xbee"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=1000, interval=350, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task09(riot_ctrl):
    nodes = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(2, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
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
        out = pinger.ping6(
            pinged_addr, count=200, interval=0, packet_size=1232, async_=True
        )
        futures.append(out)
    wait_for_futures(futures)

    check_pktbuf(*nodes)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task10(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, TASK10_APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, TASK10_APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
    )

    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=200, interval=600, packet_size=2048)
    if 10 < res['stats']['packet_loss'] <= 100:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/issues/142#issuecomment-561677974"  # noqa: E501
        )
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes',
    [pytest.param(['nrf52840dk', 'iotlab-m3', 'iotlab-m3'], "saclay")],
    indirect=['nodes'],
)
def test_task11(riot_ctrl):
    try:
        nodes = (
            riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(2, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        )
    except subprocess.CalledProcessError:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/pull/198#issuecomment-758522278"  # noqa: E501
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
        out = pinger.ping6(
            pinged_addr, count=200, interval=0, packet_size=1232, async_=True
        )
        futures.append(out)
    wait_for_futures(futures)

    check_pktbuf(*nodes)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'nrf52840dk'], "saclay")], indirect=['nodes']
)
def test_task12(riot_ctrl):
    try:
        pinger, pinged = (
            riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        )
    except subprocess.CalledProcessError:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/pull/198#issuecomment-758522278"  # noqa: E501
        )
    pinged_netif, _ = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 17)
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 17)

    res = ping6(pinger, "ff02::1", count=1000, interval=100, packet_size=50)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'nrf52840dk'], "saclay")], indirect=['nodes']
)
def test_task13(riot_ctrl):
    try:
        pinger, pinged = (
            riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
            riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        )
    except subprocess.CalledProcessError:
        pytest.xfail(
            "Experimental task. See also "
            # pylint: disable=C0301
            "https://github.com/RIOT-OS/Release-Specs/pull/198#issuecomment-758522278"  # noqa: E501
        )
    pinged_netif, pinged_addr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_set(pinged_netif, "channel", 26)
    assert pinged_addr.startswith("fe80::")
    pinger_netif, _ = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_set(pinger_netif, "channel", 26)

    res = ping6(pinger, pinged_addr, count=1000, interval=100, packet_size=100)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)
