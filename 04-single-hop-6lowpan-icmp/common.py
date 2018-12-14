import argparse

from testutils import Board
from mixins import GNRC, PktBuf
from time import sleep


#Declare node
class SixLoWPANNode(Board, GNRC, PktBuf):
    pass


def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, dest pktbuf sanity}:")
    for i in range(len(results)):
        print("Run {}: {} {} {}".format(i+1, packet_losses[i], results[i][1], results[i][2]))
    print("")
    print("Average packet losses: {}".format(sum(packet_losses)/len(packet_losses)))


def ping(source, dest, ip_dest, count, payload_size, delay, channel=26):
    source.reboot()
    dest.reboot()

    # Set channel
    iface = source.get_first_iface()
    source.set_chan(iface, channel)
    iface = dest.get_first_iface()
    dest.set_chan(iface, channel)

    packet_loss = source.ping(count, ip_dest.split("/")[0], payload_size, delay)

    return packet_loss, source.is_empty(), dest.is_empty()


argparser = argparse.ArgumentParser()
argparser.add_argument("--runs", "-n", help="Number of runs", type=int,
                       default=1)
argparser.add_argument("riotbase", help="Location of RIOT directory")
