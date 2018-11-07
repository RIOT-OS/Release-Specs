#! /usr/bin/env python3
import sys
import os
import argparse
sys.path.append("../testutils")

from testutils import bootstrap  # noqa: E402
from common import SingleHopNode, ping, print_results  # noqa: E402

PAYLOAD_SIZE = 0
ERROR_TOLERANCE = 1  # %
DELAY = 10  # ms

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('riotbase', nargs='?',
                   help='Location of RIOT folder')
    args = p.parse_args()
    riotbase = args.riotbase

    if not riotbase:
        p.print_help()
        sys.exit(1)

    os.chdir(os.path.join(riotbase, "tests/gnrc_udp"))

    bootstrap("native")
    N = 1
    results = []

    try:
        native_cmd = "make PORT={} BOARD=native term"
        source = SingleHopNode(native_cmd.format("tap0"))
        dest = SingleHopNode(native_cmd.format("tap1"))
        for i in range(N):
            ip_dest = "ff02::1/64"
            count = 1000

            packet_loss = ping(source, dest, ip_dest, count, PAYLOAD_SIZE, DELAY)
            results.append(packet_loss)

            assert(packet_loss < ERROR_TOLERANCE * count)
            print("OK")

    except Exception as e:
        print(str(e))
        print("Test failed!")
        source.stop()
        dest.stop()
        sys.exit(1)
    finally:
        source.stop()
        dest.stop()

    print_results(results)
