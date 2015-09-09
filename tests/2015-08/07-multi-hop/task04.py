#!/usr/bin/env python3

import pexpect
import os
import sys
import time
import IOTLABHelper
import math
import itertools

IOTLAB_ARCH = "m3"
IOTLAB_SITE = "grenoble"
IOTLAB_EXP_NAME = "RIOT_EXP_RPL_UDP_TEST"
IOTLAB_EXP_DUR = 5
IOTLAB_NODES = 20
PORT = 1337
nodesStr = None

def testUDP(helper, nodes):
    globalIPFormat = "dead:beef::{0}"

    for n in nodes:
        helper.startUDPServer(n, IOTLAB_ARCH, PORT)

    ret = True
    for a, b in itertools.permutations(nodes, 2):
        print("Send UDP from node {0} to node {1}".format(a[0][0], b[0][0])
        p = 0.0
        for i in range(20):
            if not helper.sendUDP(globalIPFormat.format(format(a[0][0], 'x')), \
                                  globalIPFormat.format(format(b[0][0], 'x')),\
                                  PORT, IOTLAB_ARCH, a[0]):
                p += 1.0
        p /= 20
        if (p < 0.1):
            print("Sent successfully with packet loss of {0}%".format(p*100))
        else:
            ret = False
        print("")
    return ret

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory> [nodes]" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])
    if len(sys.argv) == 3:
        nodesStr = sys.argv[2]

os.chdir("examples/gnrc_networking")

print("Run task #04")

helper = IOTLABHelper.IOTLABHelper()

testbed = helper.startExperiment(IOTLAB_EXP_NAME, IOTLAB_EXP_DUR, IOTLAB_NODES, IOTLAB_SITE, IOTLAB_ARCH, nodesStr)
if testbed == None:
    sys.exit(1)

availableNodes = helper.probeForNodes()
print("Available nodes: {0}".format([v[0] for v in availableNodes]))

if not helper.configureIPAddresses("dead:beef::{0}", IOTLAB_ARCH, [availableNodes[0]]):
    print("Error while configuring IP addresses")
    sys.exit(1)

for n in availableNodes:
    if not helper.rplInit(n, IOTLAB_ARCH, 7):
        print("Error initializing RPL")
        sys.exit(1)

helper.rplRoot(availableNodes[0], IOTLAB_ARCH, 1, "dead:beef::{0}".format(format(availableNodes[0][0], 'x')))

print("Waiting for 20 seconds so that RPL can build the DODAG")
time.sleep(20)

rplNodes = helper.getRplNodes(1, "dead:beef::{0}".format(format(availableNodes[0][0], 'x')))

if not testUDP(helper, rplNodes):
    print("Error while communicating with UDP")
    sys.exit(1)

print("SUCCESS")
