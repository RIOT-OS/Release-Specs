#!/usr/bin/env python

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Provides a server that ignores a configurable number of confirmable message
message attempts. Provides a /time resource.

Usage:
    usage: con_ignore_server.py [-h] -i IGNORES
    optional arguments:
      -h, --help  show this help message and exit
      -i IGNORES  count of requests to ignore
      
Example:

Ignores initial request and first retry. Responds on second retry.

$ PYTHONPATH="/home/kbee/src/soscoap" ./con_ignore_server.py -i 2
"""

from   argparse import ArgumentParser
import datetime
from   soscoap.server   import CoapServer, IgnoreRequestException

class ConIgnoreServer(object):
    def __init__(self, ignores):
        """Pass in count of confirmable messages to ignore."""
        self._server = CoapServer(port=5683)
        self._server.registerForResourceGet(self._getResource)
        self._ignores = ignores

    def _getResource(self, resource):
        """Sets the value for the provided resource, for a GET request."""
        if resource.path == '/time':
            if self._ignores > 0:
                self._ignores = self._ignores - 1
                raise IgnoreRequestException
                return
            else:
                resource.type  = 'string'
                now = datetime.datetime.now()
                resource.value = now.strftime("%Y-%m-%d %H:%M").encode('ascii')
        else:
            raise NotImplementedError('Unknown path')
            return

    def start(self):
        self._server.start()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', dest='ignores', type=int,
                        help='count of requests to ignore')

    args = parser.parse_args()

    server = ConIgnoreServer(args.ignores)
    server.start()


