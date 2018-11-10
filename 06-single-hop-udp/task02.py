#! /usr/bin/env python3
# Copyright (C) 2018 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import sys
import os

PORT            = 61616
COUNT           = 1000
PAYLOAD_SIZE    = 1024
DELAY           = 1000  # ms
ERROR_TOLERANCE = 5     # %


def task02(riotbase, runs=1):
    os.chdir(os.path.join(riotbase, "tests/gnrc_udp"))
    try:
        exp = IoTLABExperiment("RIOT-release-test-06-01",
                               [IoTLABNode(site="lille",
                                           extra_modules=["gnrc_pktbuf_cmd"]),
                                IoTLABNode(site="lille",
                                           extra_modules=["gnrc_pktbuf_cmd"])])
    except Exception as e:
        print(str(e))
        print("Can't start experiment")
        return

    try:
        addrs = exp.nodes_addresses
        iotlab_cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
        source = SixLoWPANNode(iotlab_cmd.format(addrs[0]))
        dest = SixLoWPANNode(iotlab_cmd.format(addrs[1]))
        results = []

        for run in range(runs):
            print("Run {}/{}: ".format(run + 1, runs), end="")
            packet_loss, buf_source, buf_dest = udp_send(source, dest,
                                                         dest.get_ip_addr(),
                                                         PORT, COUNT,
                                                         PAYLOAD_SIZE, DELAY)
            results.append([packet_loss, buf_source, buf_dest])

            assert(packet_loss < ERROR_TOLERANCE)
            assert(buf_source)
            assert(buf_dest)
            print("OK")
        print_results(results)
    except Exception as e:
        print("FAILED")
        print(str(e))
    finally:
        exp.stop()


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 "../", "testutils"))
    from iotlab import IoTLABNode, IoTLABExperiment
    from common import argparser, SixLoWPANNode, udp_send, print_results

    args = argparser.parse_args()
    task02(**vars(args))
