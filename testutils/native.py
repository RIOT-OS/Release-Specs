"""
Helpers for native
"""

import re
import subprocess


TAP_MASTER_C = re.compile(r"^\d+:\s+(?P<tap>[^:]+):.+master\s+(?P<master>\S+)?")
TAP_LINK_LOCAL_C = re.compile(
    r"inet6\s+(?P<link_local>fe80:[0-9a-f:]+)/\d+\s+scope\s+link"
)


def _run_check(cmd, shell=False):
    try:
        subprocess.check_call(
            cmd, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def command_exists(cmd):
    # command usually is a shell build-in so run it in shell
    return _run_check(' '.join(["command", "-v", cmd]), shell=True)


def _check_bridged(ip_link_output, taps):
    """
    Checks "ip link" output if a given list of TAP interfaces are in the same
    bridge

    >>> _check_bridged("", ["tap0", "tap1"])
    False
    >>> _check_bridged(
    ...      "49: tap0: <...> mtu 1500 ... master tapbr0 state ...\\n"
    ...      "     link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff\\n"
    ...      "50: tap1: <...> mtu 1500 ... master tapbr0 state ...\\n"
    ...      "     link/ether da:27:1d:a8:64:23 brd ff:ff:ff:ff:ff:ff\\n",
    ...      ["tap0", "tap1"])
    True
    >>> _check_bridged(
    ...      "50: tap1: <...> mtu 1500 ... master tapbr0 state ...\\n"
    ...      "     link/ether da:27:1d:a8:64:23 brd ff:ff:ff:ff:ff:ff\\n",
    ...      ["tap0", "tap1"])
    False
    >>> _check_bridged(
    ...      "50: tap1: <...> mtu 1500 ... master tapbr0 state ...\\n"
    ...      "     link/ether da:27:1d:a8:64:23 brd ff:ff:ff:ff:ff:ff\\n"
    ...      "60: tap0: <...> mtu 1500 qdisc fq_codel state ...\\n"
    ...      "     link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff\\n",
    ...      ["tap0", "tap1"])
    False
    """
    taps_in_bridges = set()
    tap_bridges = set()
    for line in ip_link_output.splitlines():
        m = TAP_MASTER_C.match(line)
        if m is not None and m.group("tap") in taps:
            taps_in_bridges.add(m.group("tap"))
            tap_bridges.add(m.group("master"))
    return set(taps) == taps_in_bridges and len(tap_bridges) == 1


def ip_addr_add(iface, addr):
    subprocess.check_call(["ip", "addr", "add", addr, "dev", iface])


def ip_addr_del(iface, addr):
    subprocess.run(
        ["ip", "addr", "del", addr, "dev", iface],
        stderr=subprocess.DEVNULL,
        check=False,
    )


def ip_route_add(iface, route, via=None):
    cmd = ["ip", "route", "add", route]
    if via:
        cmd += ["via", via]
    cmd += ["dev", iface]
    subprocess.check_call(cmd)


def ip_route_del(iface, route, via=None):
    cmd = ["ip", "route", "del", route]
    if via:
        cmd += ["via", via]
    cmd += ["dev", iface]
    subprocess.run(cmd, stderr=subprocess.DEVNULL, check=False)


def ip_link(iface=None):
    cmd = ["ip", "link", "show"]
    if iface is not None:
        cmd.append(iface)
    return subprocess.check_output(cmd).decode()


def bridged(taps):
    """
    Checks if a list of TAP interface `taps` are all in the same bridge
    (and exist)
    """
    return _check_bridged(ip_link(), taps)


def interface_exists(iface):
    return _run_check(["ip", "link", "show", iface])


def get_link_local(iface):
    out = subprocess.check_output(["ip", "a", "s", "dev", iface]).decode()
    for line in out.splitlines():
        m = TAP_LINK_LOCAL_C.search(line)
        if m is not None:
            return m.group("link_local")
    return None


def bridge(tap):
    """
    Get the bridge a TAP interface is assigned to. If it is not assigned to a
    bridge, the TAP interface itself is returned.
    """
    out = ip_link(tap)
    for line in out.splitlines():
        m = TAP_MASTER_C.match(line)
        if m is not None and m.group("tap") == tap:
            return m.group("master")
    return tap


def get_ping_cmd():
    if command_exists("ping6"):
        ping_cmd = "ping6"
    elif command_exists("ping"):
        ping_cmd = "ping -6"
    else:
        raise FileNotFoundError("No ping command found on host machine")
    return ping_cmd
