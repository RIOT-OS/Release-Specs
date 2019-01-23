#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Test nanocoap Block2 server response to GET request

Expected result: aiocoap prints response code 2.05 and payload

Usage:
    usage: task04.py [-h] -r HOST [-b BLOCK_SIZE]

    optional arguments:
      -h, --help     show this help message and exit
      -r HOST        remote host for URI
      -b BLOCK_SIZE  one of 16, 32, 64, ..., 1024

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./task04.py -r [fe80::200:bbff:febb:2%tap0]

Result: 2.05 Content
b'This is RIOT (Version: 2018.04-devel-3264-g99ae4-gazelle-2018.10-branch)
running on a native board with a native MCU.'
"""

import logging
import asyncio
import math
from argparse import ArgumentParser
from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main(host, block_size):
    # create async context and wait a couple of seconds
    context = await Context.create_client_context()
    await asyncio.sleep(2)

    request = Message(code=GET, uri='coap://{0}/riot/ver'.format(host))

    block_exp = round(math.log(block_size, 2)) - 4
    request.opt.block2 = optiontypes.BlockOption.BlockwiseTuple(0, 0, block_exp)

    response = await context.request(request).response

    print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')
    parser.add_argument('-b', dest='block_size', type=int, default=32,
                        help='one of 16, 32, 64, ..., 1024')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host, args.block_size))
