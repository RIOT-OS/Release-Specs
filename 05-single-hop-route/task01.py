#! /usr/bin/env python3
import sys
import os
import argparse
sys.path.append("../testutils")

from testutils import bootstrap  # noqa: E402
from common import SingleHopNode, single_hop_run, print_results  # noqa: E402

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
    N = 3
    results = []

    try:
        native_cmd = "make PORT={} BOARD=native term"
        source = SingleHopNode(native_cmd.format("tap0"))
        dest = SingleHopNode(native_cmd.format("tap1"))

        ip_src = "affe::2/64"
        ip_dest = "beef::1/64"
        src_route = "::"
        dest_route = "::"
        disable_rdv = True
        count = 100
        tolerance = 1

        for i in range(N):
            source.reboot()
            dest.reboot()

            packet_loss, buf_source, buf_dest = single_hop_run(
                    source, dest, ip_src, ip_dest, src_route,
                    dest_route, disable_rdv, count)
            results.append([packet_loss, buf_source, buf_dest])

            assert(packet_loss < tolerance)
            assert(buf_source)
            assert(buf_dest)
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
