from testutils import Board
from mixins import GNRC, PktBuf
from time import sleep

PAYLOAD_SIZE = 1024
DELAY = 10

#Declare node
class SingleHopNode(Board, GNRC, PktBuf):
    pass

def print_results(results):
    print("Summary of packet losses:")
    for i in range(len(results)):
        print("Run {}: {}".format(i+1, results[i]))
    print("")
    print("Average packet losses: {}".format(sum(results)/len(results)))

def single_hop_run(source, dest, ip_src, ip_dest, src_route, dest_route, disable_rdv, count):
    source.reboot()
    dest.reboot()

    #buf_start = [source.extract_unused(), dest.extract_unused()]

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

    return source.ping(count, ip_dest.split("/")[0], PAYLOAD_SIZE, DELAY)
    #buf_end = [source.extract_unused(), dest.extract_unused()]

    #pktbuf_diff = [buf_start[i]==buf_end[i] for i in range(2)]
    #results.append([packet_loss, pktbuf_diff])

    #assert(sum(pktbuf_diff) == 2)

