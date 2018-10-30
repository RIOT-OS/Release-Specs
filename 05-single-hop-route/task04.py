#! /usr/bin/env python3
import sys
import os
import argparse
sys.path.append("../testutils")

from testutils import Board
from iotlab import create_experiment, stop_experiment, get_nodes_addresses
from common import SingleHopNode, single_hop_run, print_results

p = argparse.ArgumentParser()
p.add_argument('riotbase', nargs='?',
               help='Location of RIOT folder')
args = p.parse_args()
riotbase = args.riotbase

if not riotbase:
    p.print_help()
    sys.exit(1)

os.chdir(os.path.join(riotbase, "tests/gnrc_udp"))

#Create IoTLAB experiment (TODO: Return addresses)
exp_id = create_experiment(2)

N = 10
results = []

try:
    addr = get_nodes_addresses(exp_id)
    iotlab_cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
    source = SingleHopNode(iotlab_cmd.format(addr[0]))
    dest = SingleHopNode(iotlab_cmd.format(addr[1]))
    for i in range(N):
        source.reboot()
        dest.reboot()

        ip_src =  None
        ip_dest =  "beef::1/64"
        src_route = "::"
        dest_route = "::"
        disable_rdv = True
        count = 10
        tolerance = 1

        packet_loss, buf_source, buf_dest = single_hop_run(source, dest, ip_src, ip_dest, src_route, dest_route, disable_rdv, count)
        results.append([packet_loss, buf_source, buf_dest])

        assert(packet_loss < tolerance)
        assert(buf_source == True)
        assert(buf_dest == True)
        print("OK")

except Exception as e:
    print(str(e))
    print("Test failed!")
    pass

stop_experiment(exp_id)
print_results(results)
