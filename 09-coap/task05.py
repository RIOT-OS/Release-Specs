#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Test gcoap Observe implementation

Acts as client and observer for gcoap Observe server for /cli/stats resource.
Also acts as server for /time resource. gcoap requests time from aiocoap, which
updates gcoap's /cli/stats resource. This update triggers gcoap to send a
notification to aiocoap.

Expected result: aiocoap prints response code 2.05 and payload for initial
response to Observe request, and for following notification.

Usage:
    usage: task05.py [-h] -r HOST

    optional arguments:
      -h, --help  show this help message and exit
      -r HOST     remote host for URI

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./task05.py -r [fd00:bbbb::2]

First response: <aiocoap.Message at 0x7f84dfa11c18: Type.ACK 2.05 Content
(MID 21466, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'0'

[gcoap requests /time]

Next result: <aiocoap.Message at 0x7f84dfa15240: Type.NON 2.05 Content
(MID 17807, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'1'

Loop ended, wait 10 sec
"""

import logging
import asyncio
import datetime
from argparse import ArgumentParser

import aiocoap.resource as resource
from aiocoap import *

logging.basicConfig(level=logging.INFO)

class TimeResource(resource.Resource):
    """Handle GET for clock time."""

    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        msg = Message(payload=payload)
        msg.opt.content_format = 0
        return msg

async def main(host):
    # setup server resources
    root = resource.Site()
    root.add_resource(('time',), TimeResource())

    context = await Context.create_server_context(root)

    msg = Message(code=GET, uri=f'coap://{host}/cli/stats', observe=0)
    req = context.request(msg)

    resp = await req.response
    print(f"First response: {resp}\n{resp.payload!r}")

    async for resp in req.observation:
        print(f"Next result: {resp}\n{resp.payload!r}")

        req.observation.cancel()
        break

    print("Loop ended, wait 10 sec")
    await asyncio.sleep(10)

if __name__ == "__main__":
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host))
