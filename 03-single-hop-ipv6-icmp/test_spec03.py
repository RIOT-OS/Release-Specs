import sys
import time

import pexpect
import pexpect.replwrap
import pytest

from riotctrl_shell.gnrc import GNRCICMPv6Echo, GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig

from testutils.asyncio import wait_for_futures, timeout_futures
from testutils.native import bridged, bridge, get_ping_cmd, interface_exists
from testutils.shell import ping6, pktbuf, lladdr


APP = 'tests/gnrc_udp'
TASK05_NODES = 11
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCPktbufStats):
    pass


@pytest.mark.skipif(not bridged(["tap0", "tap1"]),
                    reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, port='tap0'),
        riot_ctrl(1, APP, Shell, port='tap1'),
    )

    res = ping6(pinger, "ff02::1", count=1000, packet_size=0, interval=10)
    assert res['stats']['packet_loss'] < 1

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.skipif(not bridged(["tap0", "tap1"]),
                    reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, port='tap0'),
        riot_ctrl(1, APP, Shell, port='tap1'),
    )

    _, pinged_addr = lladdr(pinged.ifconfig_list())
    assert pinged_addr.startswith("fe80::")

    res = ping6(pinger, pinged_addr,
                count=1000, interval=100, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.skipif(not bridged(["tap0", "tap1"]),
                    reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, port='tap0'),
        riot_ctrl(1, APP, Shell, port='tap1'),
    )

    _, pinged_addr = lladdr(pinged.ifconfig_list())
    assert pinged_addr.startswith("fe80::")

    res = ping6(pinger, pinged_addr,
                count=3600, interval=1000, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.sudo_only      # ping -f requires root
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'] * TASK05_NODES)],
                         indirect=['nodes'])
def test_task04(riot_ctrl, log_nodes):
    node = riot_ctrl(0, APP, Shell, port='tap0')
    pingers = [pexpect.replwrap.bash() for _ in range(10)]

    _, pinged_addr = lladdr(node.ifconfig_list())
    assert pinged_addr.startswith("fe80::")
    iface = bridge('tap0')
    pinged_addr += "%{}".format(iface)
    ping_cmd = get_ping_cmd()

    futures = []
    try:
        for pinger in pingers:
            if log_nodes:
                pinger.child.logfile = sys.stdout
            out = pinger.run_command("{ping_cmd} -f -s 1452 {pinged_addr}"
                                     # pipe to /dev/null because output can go
                                     # into MiB of data ;-)
                                     " 2>&1 > /dev/null"
                                     .format(ping_cmd=ping_cmd,
                                             pinged_addr=pinged_addr),
                                     async_=True, timeout=60 * 60)
            futures.append(out)
        timeout_futures(futures, 60 * 60)
    finally:
        for pinger in pingers:
            # interrupt prevailing `ping6`s
            pinger.child.sendintr()

    time.sleep(60)
    assert pktbuf(node).is_empty()


@pytest.mark.xfail(reason="See https://github.com/RIOT-OS/RIOT/issues/12565")
@pytest.mark.skipif(not bridged(["tap{}".format(i)
                                 for i in range(TASK05_NODES)]),
                    reason="tap0 to tap10 are not bridged")
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'] * TASK05_NODES)],
                         indirect=['nodes'])
def test_task05(nodes, riot_ctrl):
    nodes = [
        riot_ctrl(i, APP, Shell, port='tap{}'.format(i))
        for i in range(len(nodes))
    ]

    async def finish_task05(pinger, future):
        await future
        print(pinger.riotctrl.env.get("PORT"), "done")

    _, pinged_addr = lladdr(nodes[0].ifconfig_list())
    assert pinged_addr.startswith("fe80::")

    futures = []
    for pinger in nodes[1:]:
        out = pinger.ping6(pinged_addr,
                           count=100000, interval=0, packet_size=1452,
                           async_=True)
        futures.append(finish_task05(pinger, out))
    wait_for_futures(futures)

    time.sleep(120)
    for node in reversed(nodes):
        # add print to know which node's packet buffer is not empty on error
        print("check pktbuf on", node.riotctrl.env.get("PORT"))
        assert pktbuf(node).is_empty()


@pytest.mark.skipif(not bridged(["tap0", "tap1"]),
                    reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task06(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, port='tap0'),
        riot_ctrl(1, APP, Shell, port='tap1'),
    )

    _, pinged_addr = lladdr(pinged.ifconfig_list())
    assert pinged_addr.startswith("fe80::")

    res = ping6(pinger, pinged_addr,
                count=1000, interval=100, packet_size=2048)
    assert res['stats']['packet_loss'] < 1
    time.sleep(60)

    assert pktbuf(pinged).is_empty()
    assert pktbuf(pinger).is_empty()
