# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Utilities for tests
"""

import pytest
import pexpect
import os
import signal
import logging

class ExpectHost():
    """
    A networking host wrapped in a pexpect spawn.

    The pexpect spawn object itself is available as the 'term' attribute.
    """

    def __init__(self, folder, term_cmd, timeout=10):
        self.folder = folder
        self.term = None
        self.term_cmd = term_cmd
        self.timeout = timeout

    def connect(self):
        """
        Starts OS host process.

        :return: pexpect spawn object; the 'term' attribute for ExpectHost
        """
        if self.folder:
            os.chdir(self.folder)
        
        self.term = pexpect.spawn(self.term_cmd, codec_errors='replace',
                                  timeout=self.timeout)
        return self.term

    def disconnect(self):
        """Kill OS host process"""
        try:
            os.killpg(os.getpgid(self.term.pid), signal.SIGKILL)
        except ProcessLookupError:
            logging.info("Process already stopped")

    def send_recv(self, out_text, in_text):
        """Sends the given text to the host, and expects the given text
           response."""
        self.term.sendline(out_text)
        self.term.expect(in_text, self.timeout)


@pytest.fixture
def gcoap_example():
    """
    Runs the RIOT gcoap CLI example as an ExpectHost.
    """
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/gcoap'), 'make term')
    term = host.connect()
    term.expect('gcoap .* app')

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::2/64',
                   'success:')
    yield host

    # teardown
    host.disconnect()
