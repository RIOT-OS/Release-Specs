from testutils import Board
from mixins import GNRC, PktBuf
from time import sleep

PAYLOAD_SIZE = 1024
DELAY = 10


# Declare node
class SingleHopNode(Board, GNRC, PktBuf):
    pass


def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, \
            dest pktbuf sanity}:")

    for i in range(len(results)):
        print("Run {}: {} {} {}".format(
            i+1, packet_losses[i], results[i][1], results[i][2]))

    print("")
    print("Average packet losses: {}".format(
        sum(packet_losses)/len(packet_losses)))


def single_hop_run(source, dest, ip_src, ip_dest,
                   src_route, dest_route, disable_rdv, count):
    source.reboot()
    dest.reboot()

    # Get useful information
    iface = source.get_first_iface()
    ip_src_ll = dest.get_ip_addr()
    ip_dest_ll = source.get_ip_addr()

    if disable_rdv:
        # Disable router advertisement
        source.disable_rdv(iface)
        dest.disable_rdv(iface)

    # Add static IP addresses
    if(ip_src):
        source.add_ip(iface, ip_src)

    if(ip_dest):
        dest.add_ip(iface, ip_dest)

    # Sleep 1 second before sending data
    sleep(1)

    # Add nib routes
    source.add_nib_route(iface, src_route, ip_src_ll)
    dest.add_nib_route(iface, dest_route, ip_dest_ll)

    packet_loss = source.ping(
            count, ip_dest.split("/")[0], PAYLOAD_SIZE, DELAY)

    return (packet_loss, source.is_empty(), dest.is_empty())
