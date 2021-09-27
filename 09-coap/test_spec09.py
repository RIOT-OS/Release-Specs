import asyncio
import datetime
import re
import math
import os
import subprocess
import time

import aiocoap
import aiocoap.resource
import pytest

from riotctrl_shell.netif import Ifconfig
from riotctrl_shell.cord_ep import CordEp, CordEpRegistrationInfoParser

from testutils.asyncio import timeout_futures, wait_for_futures
from testutils.native import bridge, interface_exists, \
                             ip_addr_add, ip_addr_del
from testutils.shell import lladdr


SPEC_PATH = os.path.dirname(os.path.realpath(__file__))
HOST_ULA = "fd00:bbbb::1"
NODE_ULA = "fd00:bbbb::2"
TAP = 'tap0'


pytestmark = pytest.mark.rc_only()


class Shell(Ifconfig, CordEp):
    # pylint: disable=R0913
    def coap_get(self, addr, port, resource, confirmable=False, timeout=-1,
                 async_=False):
        cmd = "coap get "
        if confirmable:
            cmd += "-c "
        cmd += f"{addr} {port:d} {resource}"
        return self.cmd(cmd, timeout=timeout, async_=async_)


# pylint: disable=R0903
class TimeResource(aiocoap.resource.Resource):
    """Handle GET for clock time."""
    # pylint: disable=W0613, disable=R0201
    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        msg = aiocoap.Message(payload=payload)
        # pylint: disable=E0237
        msg.opt.content_format = 0
        return msg


async def coap_server():
    # setup server resources
    root = aiocoap.resource.Site()
    root.add_resource(('time',), TimeResource())

    return await aiocoap.Context.create_server_context(root)


def setup_function(function):
    if function.__name__ in ["test_task01", "test_task02", "test_task05"]:
        host_netif = bridge(TAP)
        ip_addr_add(host_netif, f"{HOST_ULA}/64")


def teardown_function(function):
    if function.__name__ in ["test_task01", "test_task02", "test_task05"]:
        host_netif = bridge(TAP)
        ip_addr_del(host_netif, f"{HOST_ULA}/64")


# sudo required for function setup (address configuration of interface)
@pytest.mark.sudo_only
@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl, log_nodes):
    node = riot_ctrl(0, 'examples/cord_ep', Shell, port=TAP)

    node_netif, _ = lladdr(node.ifconfig_list())
    node.ifconfig_add(node_netif, NODE_ULA)
    # pylint: disable=R1732
    aiocoap_rd = subprocess.Popen(
        ["aiocoap-rd"],
        stdout=None if log_nodes else subprocess.DEVNULL,
        stderr=None if log_nodes else subprocess.DEVNULL,
    )
    try:
        res = node.cord_ep_register(f"[{HOST_ULA}]")
        parser = CordEpRegistrationInfoParser()
        core_reg = parser.parse(res)
        if core_reg["ltime"] > 300:
            pytest.xfail("CoRE RD lifetime is configured for {}s (> 5min). "
                         "That's way to long for a test!"
                         .format(core_reg["ltime"]))
        time.sleep(core_reg["ltime"])
    finally:
        aiocoap_rd.terminate()
        aiocoap_rd.wait()
    node.riotctrl.term.expect_exact(
        "RD endpoint event: successfully updated client registration",
    )


# sudo required for function setup (address configuration of interface)
@pytest.mark.sudo_only
@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.parametrize('nodes,start_server,expected',
                         [pytest.param(['native'], True, 1),
                          pytest.param(['native'], False, 0)],
                         indirect=['nodes'])
def test_task02(riot_ctrl, start_server, expected):
    node = riot_ctrl(0, 'examples/gcoap', Shell, port=TAP)

    node_netif, _ = lladdr(node.ifconfig_list())
    node.ifconfig_add(node_netif, NODE_ULA)

    async def run_task02_server():
        server = await coap_server()
        # kill server after 10 seconds, then it has enough time to respond to
        # first retry
        await asyncio.sleep(10)
        await server.shutdown()

    res = node.coap_get(HOST_ULA, 5683, "/time", confirmable=True)
    time.sleep(1)
    if start_server:
        wait_for_futures([run_task02_server()])
    res = node.riotctrl.term.expect([
        r"gcoap: timeout for msg ID \d+",
        r"gcoap: response Success, code 2.05, \d+ bytes",
    ], timeout=100)
    assert res == expected


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    node = riot_ctrl(0, 'examples/nanocoap_server', Shell, port=TAP)
    host_netif = bridge(TAP)

    # can't use shell interactions here, as there is no shell
    node.riotctrl.term.expect(r"inet6 addr:\s+(fe80::[0-9a-f:]+)")
    node_lladdr = node.riotctrl.term.match.group(1)

    async def client(host, block_size):
        # create async context and wait a couple of seconds
        context = await aiocoap.Context.create_client_context()
        await asyncio.sleep(2)

        payload = (
            b'If one advances confidently in the direction of his dreams,'
            b' he will meet with a success unexpected in common hours.'
        )

        # pylint: disable=E1101
        request = aiocoap.Message(code=aiocoap.POST, payload=payload,
                                  uri=f'coap://{host}/sha256')

        block_exp = round(math.log(block_size, 2)) - 4
        # pylint: disable=E0237
        request.opt.block1 = aiocoap.optiontypes.BlockOption.BlockwiseTuple(
            0, 0, block_exp
        )

        return await context.request(request).response

    for block_size in range(16, 1024 + 1, 16):
        print("Testing block size", block_size)
        response = asyncio.get_event_loop().run_until_complete(
            client(f"[{node_lladdr}%{host_netif}]", block_size)
        )
        assert str(response.code) == "2.04 Changed"
        # payload is a sha256 digest
        assert re.match("^[0-9A-Fa-f]{64}$", response.payload.decode())


@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task04(riot_ctrl):
    node = riot_ctrl(0, 'examples/nanocoap_server', Shell, port=TAP)
    host_netif = bridge(TAP)

    # can't use shell interactions here, as there is no shell
    node.riotctrl.term.expect(r"inet6 addr:\s+(fe80::[0-9a-f:]+)")
    node_lladdr = node.riotctrl.term.match.group(1)

    async def client(host, block_size):
        # create async context and wait a couple of seconds
        context = await aiocoap.Context.create_client_context()
        await asyncio.sleep(2)

        # pylint: disable=E1101
        request = aiocoap.Message(code=aiocoap.GET,
                                  uri=f'coap://{host}/riot/ver')

        block_exp = round(math.log(block_size, 2)) - 4
        # pylint: disable=E0237
        request.opt.block2 = aiocoap.optiontypes.BlockOption.BlockwiseTuple(
            0, 0, block_exp
        )

        return await context.request(request).response

    for block_size in range(16, 1024 + 1, 16):
        print("Testing block size", block_size)
        response = asyncio.get_event_loop().run_until_complete(
            client(f"[{node_lladdr}%{host_netif}]", block_size)
        )
        assert str(response.code) == "2.05 Content"
        assert re.search(r"This is RIOT \(Version: .*\) running on a "
                         r"native board with a native MCU\.",
                         response.payload.decode())


# sudo required for function setup (address configuration of interface)
@pytest.mark.sudo_only
@pytest.mark.skipif(not interface_exists("tap0"),
                    reason="tap0 does not exist")
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task05(riot_ctrl):
    node = riot_ctrl(0, 'examples/gcoap', Shell, port=TAP)

    node_netif, _ = lladdr(node.ifconfig_list())
    node.ifconfig_add(node_netif, NODE_ULA)
    responses = []

    async def client_server(host):
        context = await coap_server()

        # pylint: disable=E1101
        msg = aiocoap.Message(code=aiocoap.GET,
                              uri=f'coap://{host}/cli/stats',
                              observe=0)
        req = context.request(msg)

        resp = await req.response
        responses.append(resp)

        res = node.coap_get(HOST_ULA, 5683, "/time", confirmable=True)
        assert re.search(r"gcoap_cli: sending msg ID \d+, \d+ bytes", res)

        async for resp in req.observation:
            responses.append(resp)

            req.observation.cancel()
            break
        await context.shutdown()

    timeout_futures([client_server(f'[{NODE_ULA}]')], timeout=2)
    node.riotctrl.term.expect(r"gcoap: response Success, code 2.05, \d+ bytes")
    assert len(responses) == 2
    for i, response in enumerate(responses):
        assert str(response.code) == "2.05 Content"
        assert int(response.payload) == i
