"""
Extra shell interactions and parsers not covered by `riotctrl_shell` and
convenience functions for the use of ShellInteractions and
ShellInteractionParsers
"""

import time

import pexpect
from riotctrl.shell import ShellInteraction

from riotctrl_shell.gnrc import GNRCICMPv6EchoParser, GNRCPktbufStatsParser
from riotctrl_shell.netif import IfconfigListParser

PARSERS = {
    "ping6": GNRCICMPv6EchoParser(),
    "pktbuf": GNRCPktbufStatsParser(),
    "ifconfig": IfconfigListParser(),
}


class GNRCLoRaWANSend(ShellInteraction):
    """
    Shell interaction for

    - $RIOTBASE/examples/networking/gnrc/lorawan

    As the `send` shell command is application specific, a central
    ShellInteraction in `riotctrl_shell` does not make much sense
    """

    @ShellInteraction.check_term
    def txtsnd(self, netif, payload, port=1, timeout=-1):
        self.cmd(
            f"txtsnd {netif} {port:02x} \"{payload}\"", timeout=timeout, async_=False
        )

        exp = self.riotctrl.term.expect([pexpect.TIMEOUT, r"~~ PKT"], timeout=timeout)

        return bool(exp)


def ping6(pinger, hostname, count, packet_size, interval):
    out = pinger.ping6(
        hostname, count=count, packet_size=packet_size, interval=interval
    )
    return PARSERS["ping6"].parse(out)


def pktbuf(node):
    out = node.pktbuf_stats()
    res = PARSERS["pktbuf"].parse(out)
    return res


def ifconfig(node, netif=None):
    out = node.ifconfig_list(netif=netif)
    res = PARSERS["ifconfig"].parse(out)
    return res


def first_netif_and_addr_by_scope(ifconfig_out, scope, ignore_chan_0=False):
    netifs = PARSERS["ifconfig"].parse(ifconfig_out)
    for key, netif in netifs.items():
        if not ignore_chan_0 or netif.get("channel", -1) != 0:
            return (
                key,
                [
                    addr["addr"]
                    for addr in netif["ipv6_addrs"]
                    if addr["scope"] == scope
                ][0],
            )
    raise RuntimeError(f"For valid netifs found in {netifs}")


def lladdr(ifconfig_out, ignore_chan_0=False):
    return first_netif_and_addr_by_scope(
        ifconfig_out, "link", ignore_chan_0=ignore_chan_0
    )


def global_addr(ifconfig_out):
    return first_netif_and_addr_by_scope(ifconfig_out, "global")


def check_pktbuf(*nodes, wait=10):
    if wait:
        time.sleep(wait)
    for n in nodes:
        assert pktbuf(n).is_empty()


def lorawan_netif(node):
    netif = ifconfig(node)

    iface = None
    for k in netif:
        if "sf" in netif[k]:
            iface = int(k)
            break

    return iface
