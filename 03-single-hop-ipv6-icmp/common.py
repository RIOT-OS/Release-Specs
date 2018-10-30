from testutils import Board
from mixins import GNRC, PktBuf
from time import sleep

#Declare node
class SingleHopNode(Board, GNRC, PktBuf):
    pass

def print_results(results):
    print("Summary of packet losses:")
    for i in range(len(results)):
        print("Run {}: {}".format(i+1, results[i]))
    print("")
    print("Average packet losses: {}".format(sum(results)/len(results)))

def ping(source, dest, ip_dest, count, payload_size, delay):
    source.reboot()
    dest.reboot()

    sleep(1)

    return source.ping(count, ip_dest.split("/")[0], payload_size, delay)
