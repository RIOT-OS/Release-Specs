import os
import re
import sys
import subprocess


import pexpect.replwrap
import pytest

import riotctrl.shell
from riotctrl_shell.gnrc import GNRCICMPv6Echo
from riotctrl_shell.netif import Ifconfig

from testutils.native import bridge, get_link_local, get_ping_cmd, interface_exists
from testutils.shell import lladdr, ping6, GNRCUDP


GNRC_APP = 'examples/gnrc_networking'
LWIP_APP = 'tests/pkg/lwip'
pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, GNRCICMPv6Echo, GNRCUDP):
    pass


@pytest.mark.skipif(not interface_exists("tap0"), reason="tap0 does not exist")
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes', [pytest.param(['native'])], indirect=['nodes'])
def test_task01(riot_ctrl, log_nodes):
    node = riot_ctrl(0, GNRC_APP, Shell, port='tap0')
    linux = pexpect.replwrap.bash()

    node_iface, node_addr = lladdr(node.ifconfig_list())
    assert node_addr.startswith("fe80::")
    linux_iface = bridge('tap0')
    linux_addr = get_link_local(linux_iface)
    assert linux_addr.startswith("fe80::")
    ping_cmd = get_ping_cmd()

    if log_nodes:
        linux.child.logfile = sys.stdout
    out = linux.run_command(
        f"{ping_cmd} -c 20 -i .5 {node_addr}%{linux_iface}", timeout=20
    )
    m = re.search(r"\b(\d+)% packet loss", out)
    assert m is not None
    assert int(m.group(1)) < 1
    res = ping6(
        node, f"{linux_addr}%{node_iface}", count=20, interval=100, packet_size=8
    )
    assert res["stats"]["packet_loss"] < 1


@pytest.mark.flaky(reruns=1, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['nrf52840dk', 'nrf52840dk'])], indirect=['nodes']
)
def test_task03(riot_ctrl):
    # run `./compile_contiki.sh` relative to this file
    subprocess.check_call(
        ["./compile_contiki.sh"],
        cwd=os.path.dirname(os.path.realpath(__file__)),
    )

    build_path = "build/nrf52840/dk/hello-world.nrf52840"
    flashfile = f"/tmp/contiki-ng/examples/hello-world/{build_path}"

    gnrc_node, contiki_node = (
        riot_ctrl(0, GNRC_APP, Shell),
        riot_ctrl(
            1,
            'examples/hello-world',
            riotctrl.shell.ShellInteraction,
            extras={"BINFILE": flashfile},
        ),
    )

    gnrc_netif, gnrc_addr = lladdr(gnrc_node.ifconfig_list())

    # get the address of the contiki node, ie a substring after "-- "
    res = contiki_node.cmd("ip-addr")
    match = re.search("-- (.+)", res)
    assert match
    contiki_addr = match[1]

    gnrc_node.ifconfig_set(gnrc_netif, "pan_id", "abcd")

    res = contiki_node.cmd(f"ping {gnrc_addr}")
    assert f"Received ping reply from {gnrc_addr}" in res

    res = ping6(gnrc_node, contiki_addr, 3, 12, 1)
    assert res['stats']['packet_loss'] < 10


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'iotlab-m3'])], indirect=['nodes']
)
def test_task08(riot_ctrl):
    gnrc_node, lwip_node = (
        riot_ctrl(0, GNRC_APP, Shell),
        riot_ctrl(1, LWIP_APP, riotctrl.shell.ShellInteraction),
    )

    _, gnrc_addr = lladdr(gnrc_node.ifconfig_list())
    assert gnrc_addr.startswith("fe80::")
    res = lwip_node.cmd("ifconfig")
    m = re.search(r"inet6 addr:\s+(?P<addr>fe80:[0-9a-f:]+)", res)
    assert m is not None
    lwip_addr = m.group("addr")

    gnrc_node.udp_server_start(61616)

    lwip_node.cmd(f"udp send [{gnrc_addr}]:61616 012345678abcdef")
    packet_loss = gnrc_node.udp_server_check_output(count=1, delay_ms=0)
    assert packet_loss == 0
    gnrc_node.udp_server_stop()

    lwip_node.cmd("udp server start 61617")
    gnrc_node.udp_client_send(lwip_addr, 61617, "01234567")
    lwip_node.riotctrl.term.expect_exact(f"Received UDP data from [{gnrc_addr}]:61617")
    lwip_node.riotctrl.term.expect_exact(
        "00000000  " + "  ".join(hex(ord(c))[2:] for c in "01234567"), timeout=3
    )


# @pytest.mark.flaky(reruns=1, reruns_delay=30)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes', [pytest.param(['iotlab-m3', 'samr21-xpro'])], indirect=['nodes']
)
def test_task11(riot_ctrl):
    # run `./compile_contiki.sh` relative to this file
    subprocess.check_call(
        ["./compile_zephyr.sh"],
        cwd=os.path.dirname(os.path.realpath(__file__)),
    )

    build_path = "zephyr/build/zephyr/zephyr.elf"
    flashfile = f"/tmp/zephyrproject/{build_path}"

    gnrc_node, zephyr_node = (
        riot_ctrl(0, GNRC_APP, Shell),
        riot_ctrl(
            1,
            'examples/hello-world',
            riotctrl.shell.ShellInteraction,
            extras={"BINFILE": flashfile},
        ),
    )
    zephyr_node.prompt = "uart:~$ "
    
    # gnrc_netif, gnrc_addr = lladdr(gnrc_node.ifconfig_list())

    # Get the ipv6 address, expected response:
    # IPv6 support                              : enabled
    # IPv6 fragmentation support                : disabled
    # Multicast Listener Discovery support      : enabled
    # Neighbor cache support                    : enabled
    # Neighbor discovery support                : enabled
    # Duplicate address detection (DAD) support : enabled
    # Router advertisement RDNSS option support : enabled
    # 6lo header compression support            : enabled
    # Max number of IPv6 network interfaces in the system          : 1
    # Max number of unicast IPv6 addresses per network interface   : 3
    # Max number of multicast IPv6 addresses per network interface : 4
    # Max number of IPv6 prefixes per network interface            : 2

    # IPv6 addresses for interface 0x20007d60 (IEEE 802.15.4)
    # =======================================================
    # Type            State           Lifetime (sec)  Address
    # autoconf        preferred       infinite        fe80::d419:100:7ae4:9b3b/128
    # manual          preferred       infinite        2001:db8::1/128
    res = zephyr_node.cmd("net ipv6")
    match = re.search("fe80::(?P<addr>[0-9a-f:]+)/128", res)
    assert match
    zephyr_addr = f"fe80::{match[1]}"

    # Get the PAN ID, expected response: "PAN ID 43981 (0xabcd)"
    res = zephyr_node.cmd("ieee802154 get_pan_id")
    match = re.search("PAN ID (?P<pan_id>\d+) \(0x(?P<pan_id_hex>[0-9a-f]+)\)", res)
    assert match
    pan_id = match["pan_id_hex"]

    # Get the Channel, expected response: "Channel 26"
    res = zephyr_node.cmd("ieee802154 get_chan")
    match = re.search("Channel (?P<channel>\d+)", res)
    assert match
    channel = match[1]


    gnrc_netif, gnrc_addr = lladdr(gnrc_node.ifconfig_list())

    gnrc_node.ifconfig_set(gnrc_netif, "channel", channel)
    gnrc_node.ifconfig_set(gnrc_netif, "pan_id", pan_id)
    res = gnrc_node.cmd("udp server start 4242")
    assert "udp server start 4242" in res

    res = gnrc_node.cmd(f"udp send {zephyr_addr} 4242 \"RIOT Testing!\"")
    assert "Success: sent 13 byte" in res

    res = zephyr_node.riotctrl.term.readline()
    assert "Received and replied with 13 bytes" in res


