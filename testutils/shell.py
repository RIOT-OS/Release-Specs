"""
Extra shell interactions and parsers not covered by `riotctrl_shell` and
convenience functions for the use of ShellInteractions and
ShellInteractionParsers
"""

import math
import re

import pexpect
from riotctrl.shell import ShellInteraction, ShellInteractionParser

from riotctrl_shell.gnrc import GNRCICMPv6EchoParser, GNRCPktbufStatsParser
from riotctrl_shell.netif import IfconfigListParser


PARSERS = {
    "ping6": GNRCICMPv6EchoParser(),
    "pktbuf": GNRCPktbufStatsParser(),
    "ifconfig": IfconfigListParser(),
}


# pylint: disable=R0903
class GNRCUDPClientSendParser(ShellInteractionParser):
    """
    Shell interaction parser for

    - $RIOTBASE/examples/gnrc_networking
    - $RIOTBASE/tests/gnrc_udp.

    As the `udp` shell command is application specific, a central
    ShellInteraction in `riotctrl_shell` does not make much sense
    """
    def __init__(self):
        self.success_c = re.compile(r"Success:\s+sen[td]\s+"
                                    r"(?P<payload_len>\d+)\s+"
                                    r"byte(\(s\))?\s+to\s+"
                                    r"\[(?P<dst>[0-9a-f:]+(%\S+)?)\]:"
                                    r"(?P<dport>\d+)$")

    def parse(self, cmd_output):
        """
        Parses output of GNRCUDP::udp_client_send()

        >>> parser = GNRCUDPClientSendParser()
        >>> res = parser.parse("Success: send 12 byte to [fe80::1%2]:1337  \\n"
        ...                    "Success: sent 5 byte(s) to [abcd::2]:52\\n")
        >>> len(res)
        2
        >>> sorted(res[0])
        ['dport', 'dst', 'payload_len']
        >>> sorted(res[1])
        ['dport', 'dst', 'payload_len']
        >>> res[0]["payload_len"], res[1]["payload_len"]
        (12, 5)
        >>> res[0]["dst"], res[1]["dst"]
        ('fe80::1%2', 'abcd::2')
        >>> res[0]["dport"], res[1]["dport"]
        (1337, 52)
        """
        res = []
        for line in cmd_output.splitlines():
            m = self.success_c.search(line.strip())
            if m is not None:
                msg = m.groupdict()
                msg["payload_len"] = int(msg["payload_len"])
                msg["dport"] = int(msg["dport"])
                res.append(msg)
        return res


class GNRCUDP(ShellInteraction):
    """
    Shell interaction for

    - $RIOTBASE/examples/gnrc_networking
    - $RIOTBASE/tests/gnrc_udp.

    As the `udp` shell command is application specific, a central
    ShellInteraction in `riotctrl_shell` does not make much sense
    """
    @ShellInteraction.check_term
    def udp_server_start(self, port, timeout=-1, async_=False):
        res = self.cmd("udp server start {}".format(port), timeout=timeout,
                       async_=async_)
        if "Success:" not in res:
            raise RuntimeError(res)
        return res

    @ShellInteraction.check_term
    def udp_server_stop(self, timeout=-1, async_=False):
        return self.cmd("udp server stop", timeout=timeout, async_=async_)

    def udp_server_check_output(self, count, delay_ms):
        packets_lost = 0
        if delay_ms > 0:
            timeout = (delay_ms / 1000) * 10
        else:
            timeout = 1
        for _ in range(count):
            exp = self.riotctrl.term.expect([
                pexpect.TIMEOUT,
                r"Packets received:\s+\d",
                r"PKTDUMP: data received:"
            ], timeout=timeout)
            if not exp:     # expect timed out
                packets_lost += 1
            if exp < 2:
                continue
            try:
                self.riotctrl.term.expect(
                    r"~~ SNIP  0 - size:\s+\d+ byte, type: NETTYPE_UNDEF "
                    r"\(\d+\)"
                )
                self.riotctrl.term.expect(
                    r"~~ SNIP  1 - size:\s+\d+ byte, type: NETTYPE_UDP \(\d+\)"
                )
                self.riotctrl.term.expect(
                    r"~~ SNIP  2 - size:\s+40 byte, type: NETTYPE_IPV6 \(\d+\)"
                )
                self.riotctrl.term.expect(
                    r"~~ SNIP  3 - size:\s+\d+ byte, type: NETTYPE_NETIF "
                    r"\(-1\)"
                )
                self.riotctrl.term.expect(
                    r"~~ PKT\s+-\s+4 snips, total size:\s+\d+ byte"
                )
            except pexpect.TIMEOUT:
                packets_lost += 1
        return (packets_lost / count) * 100

    # pylint: disable=R0913
    @ShellInteraction.check_term
    def udp_client_send(self, dest_addr, port, payload,
                        count=1, delay_ms=1000, async_=False):
        if delay_ms:
            # wait .5 sec more per message
            timeout = math.ceil((delay_ms * count) / 1000) + (5 * (count / 10))
        else:
            # wait 1 sec per message
            timeout = count * 1
        res = self.cmd(
            "udp send {dest_addr} {port} {payload} {count} {delay_us}"
            .format(dest_addr=dest_addr, port=port, payload=payload,
                    count=count, delay_us=int(delay_ms * 1000)),
            timeout=timeout, async_=async_
        )
        if "Error:" in res:
            raise RuntimeError(res)
        return res


def ping6(pinger, hostname, count, packet_size, interval):
    out = pinger.ping6(hostname, count=count, packet_size=packet_size,
                       interval=interval)
    return PARSERS["ping6"].parse(out)


def pktbuf(node):
    out = node.pktbuf_stats()
    res = PARSERS["pktbuf"].parse(out)
    return res


def lladdr(ifconfig_out):
    netifs = PARSERS["ifconfig"].parse(ifconfig_out)
    key = next(iter(netifs))
    netif = netifs[key]
    return key, [addr["addr"] for addr in netif["ipv6_addrs"] if
                 addr["scope"] == "link"][0]
