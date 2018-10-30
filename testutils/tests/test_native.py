import pytest

import testutils.native


def test_command_exists(monkeypatch):
    monkeypatch.setattr(testutils.native.subprocess, "check_call",
                        lambda *args, **kwargs: None)
    assert testutils.native.command_exists("test")


def test_command_not_exists(monkeypatch):
    def func(*args, **kwargs):
        raise testutils.native.subprocess.CalledProcessError(1, "test")
    monkeypatch.setattr(testutils.native.subprocess, "check_call", func)
    assert not testutils.native.command_exists("test")


@pytest.mark.parametrize(
    "args",
    ((), ("test",))
)
def test_ip_link(monkeypatch, args):
    monkeypatch.setattr(testutils.native.subprocess, "check_output",
                        lambda *args, **kwargs: b"This is a test")
    assert testutils.native.ip_link(*args) == "This is a test"


def test_ip_addr_add(monkeypatch):
    monkeypatch.setattr(testutils.native.subprocess, "check_call",
                        lambda *args, **kwargs: None)
    testutils.native.ip_addr_add("test", "2001:db8::1")


def test_ip_addr_del(monkeypatch):
    monkeypatch.setattr(testutils.native.subprocess, "run",
                        lambda *args, **kwargs: None)
    testutils.native.ip_addr_del("test", "2001:db8::1")


@pytest.mark.parametrize(
    "args",
    ((), ("fe80::1",))
)
def test_ip_route_add(monkeypatch, args):
    monkeypatch.setattr(testutils.native.subprocess, "check_call",
                        lambda *args, **kwargs: None)
    testutils.native.ip_route_add("test", "2001:db8::/64", *args)


@pytest.mark.parametrize(
    "args",
    ((), ("fe80::1",))
)
def test_ip_route_del(monkeypatch, args):
    monkeypatch.setattr(testutils.native.subprocess, "run",
                        lambda *args, **kwargs: None)
    testutils.native.ip_route_del("test", "2001:db8::/64", *args)


@pytest.mark.parametrize("expected", [True, False])
def test_bridged(monkeypatch, expected):
    monkeypatch.setattr(testutils.native, "_check_bridged",
                        lambda *args, **kwargs: expected)
    assert testutils.native.bridged(["tap0", "tap1"]) == expected


def test_interface_exists(monkeypatch):
    monkeypatch.setattr(testutils.native.subprocess, "check_call",
                        lambda *args, **kwargs: None)
    assert testutils.native.interface_exists("test")


def test_interface_not_exists(monkeypatch):
    def func(*args, **kwargs):
        raise testutils.native.subprocess.CalledProcessError(1, "test")
    monkeypatch.setattr(testutils.native.subprocess, "check_call", func)
    assert not testutils.native.interface_exists("test")


def test_get_link_local(monkeypatch):
    output = """
95: tap0: ...
    link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff
    inet6 fe80::e0bc:7dff:fecb:f54f/64 scope link
       valid_lft forever preferred_lft forever"""
    monkeypatch.setattr(testutils.native.subprocess, "check_output",
                        lambda *args, **kwargs: output.encode())
    assert testutils.native.get_link_local("tap0") == \
           "fe80::e0bc:7dff:fecb:f54f"


def test_get_link_local_not_none(monkeypatch):
    output = """
95: tap0: ...
    link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff"""
    monkeypatch.setattr(testutils.native.subprocess, "check_output",
                        lambda *args, **kwargs: output.encode())
    assert testutils.native.get_link_local("tap0") is None


def test_bridge_bridged(monkeypatch):
    monkeypatch.setattr(testutils.native, "ip_link",
                        lambda *args, **kwargs: """
49: tap0: <...> mtu 1500 ... master tapbr0 state ...
     link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff
50: tap1: <...> mtu 1500 ... master tapbr0 state ...
     link/ether da:27:1d:a8:64:23 brd ff:ff:ff:ff:ff:ff
""")
    assert testutils.native.bridge("tap0") == "tapbr0"


def test_bridge_unbridged(monkeypatch):
    monkeypatch.setattr(testutils.native, "ip_link",
                        lambda *args, **kwargs: """
60: tap0: <...> mtu 1500 qdisc fq_codel state ...
     link/ether e2:bc:7d:cb:f5:4f brd ff:ff:ff:ff:ff:ff
""")
    assert testutils.native.bridge("tap0") == "tap0"


@pytest.mark.parametrize(
    "ping_cmd,expected",
    [("ping6", "ping6"), ("ping", "ping -6")]
)
def test_get_ping_cmd(monkeypatch, ping_cmd, expected):
    monkeypatch.setattr(testutils.native, "command_exists",
                        lambda cmd: cmd == ping_cmd)
    assert testutils.native.get_ping_cmd() == expected


def test_get_ping_cmd_no_ping(monkeypatch):
    monkeypatch.setattr(testutils.native, "command_exists",
                        lambda cmd: False)
    with pytest.raises(FileNotFoundError):
        testutils.native.get_ping_cmd()
