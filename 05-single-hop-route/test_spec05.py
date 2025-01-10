import pytest
from riotctrl_shell.gnrc import GNRCICMPv6Echo, GNRCIPv6NIB, GNRCPktbufStats
from riotctrl_shell.netif import Ifconfig
from testutils.native import bridged
from testutils.shell import check_pktbuf, lladdr, ping6

APP = 'examples/gnrc_networking'
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCPktbufStats, GNRCIPv6NIB):
    pass


@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native', 'native'])], indirect=['nodes']
)
def test_task01(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap0"),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap1"),
    )

    pinged_netif, pinged_lladdr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_flag(pinged_netif, "rtr_adv", False)
    pinged.ifconfig_add(pinged_netif, "beef::1/64")
    pinger_netif, pinger_lladdr = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_flag(pinger_netif, "rtr_adv", False)
    pinger.ifconfig_add(pinger_netif, "beef::2/64")

    pinged.nib_route_add(pinged_netif, "::", pinger_lladdr)
    pinger.nib_route_add(pinger_netif, "::", pinged_lladdr)

    res = ping6(pinger, "beef::1", count=100, interval=10, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    check_pktbuf(pinged, pinger)


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task02(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"]),
    )

    pinged_netif, pinged_lladdr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_add(pinged_netif, "beef::1/64")
    pinger_netif, pinger_lladdr = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_add(pinger_netif, "affe::1/120")

    pinged.nib_route_add(pinged_netif, "::", pinger_lladdr)
    pinger.nib_route_add(pinger_netif, "::", pinged_lladdr)

    res = ping6(pinger, "beef::1", count=100, interval=300, packet_size=1024)
    assert res['stats']['packet_loss'] < 10

    check_pktbuf(pinged, pinger)

@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native64', 'native64'])], indirect=['nodes']
)
def test_task03(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap0"),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap1"),
    )

    pinged_netif, pinged_lladdr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_flag(pinged_netif, "rtr_adv", False)
    pinged.ifconfig_add(pinged_netif, "beef::1/64")
    pinger_netif, pinger_lladdr = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_flag(pinger_netif, "rtr_adv", False)
    pinger.ifconfig_add(pinger_netif, "beef::2/64")

    pinged.nib_route_add(pinged_netif, "::", pinger_lladdr)
    pinger.nib_route_add(pinger_netif, "::", pinged_lladdr)

    res = ping6(pinger, "beef::1", count=100, interval=10, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    check_pktbuf(pinged, pinger)


@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native', 'native'])], indirect=['nodes']
)
def test_task04(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap0"),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap1"),
    )

    pinged_netif, pinged_lladdr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_flag(pinged_netif, "rtr_adv", False)
    pinged.ifconfig_add(pinged_netif, "beef::1/64")
    pinger_netif, pinger_lladdr = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_flag(pinger_netif, "rtr_adv", False)
    pinger.ifconfig_add(pinger_netif, "beef::2/64")

    pinged.nib_route_add(pinged_netif, "beef::/64", pinger_lladdr)
    pinger.nib_route_add(pinger_netif, "beef::/64", pinged_lladdr)

    res = ping6(pinger, "beef::1", count=10, interval=10, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    check_pktbuf(pinged, pinger)


@pytest.mark.skipif(not bridged(["tap0", "tap1"]), reason="tap0 and tap1 not bridged")
@pytest.mark.parametrize(
    'nodes', [pytest.param(['native', 'native'])], indirect=['nodes']
)
def test_task05(riot_ctrl):
    pinger, pinged = (
        riot_ctrl(0, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap0"),
        riot_ctrl(1, APP, Shell, modules=["shell_cmd_gnrc_pktbuf"], port="tap1"),
    )

    pinged_netif, pinged_lladdr = lladdr(pinged.ifconfig_list())
    pinged.ifconfig_flag(pinged_netif, "rtr_adv", False)
    pinged.ifconfig_add(pinged_netif, "beef::1/64")
    pinger_netif, pinger_lladdr = lladdr(pinger.ifconfig_list())
    pinger.ifconfig_flag(pinger_netif, "rtr_adv", False)

    pinged.nib_route_add(pinged_netif, "::", pinger_lladdr)
    pinger.nib_route_add(pinger_netif, "::", pinged_lladdr)

    res = ping6(pinger, "beef::1", count=10, interval=300, packet_size=1024)
    assert res['stats']['packet_loss'] < 1

    check_pktbuf(pinged, pinger)
