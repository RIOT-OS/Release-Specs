#!/usr/bin/env python3

import pexpect
import os
import sys
import time
import IOTLABHelper
import math

IOTLAB_ARCH = "m3"
IOTLAB_SITE = "grenoble"
IOTLAB_EXP_NAME = "RIOT_EXP_PING_TEST"
IOTLAB_EXP_DUR = 5
IOTLAB_NODES = 20
NODES = 4
PORT = 1337
IFACE = 7
nodesStr = None

def testUDP(helper, nodes, hops):
    localIPFormat = "fe80::{0}"
    globalIPFormat = "dead:beef::{0}"

    for n in nodes:
        helper.startUDPServer(n, IOTLAB_ARCH, PORT)

    for win in helper.window(sortedNodes, hops):
        print("window: {0}".format([v[0] for v in win]))
        helper.setFibRoutesInARow(win, IOTLAB_ARCH, iface, globalIPFormat)
        p = 0.0
        for i in range(20):
            if not helper.sendUDP(globalIPFormat.format(format(win[0][0], 'x')), \
                                  globalIPFormat.format(format(win[-1][0], 'x')),\
                                  PORT, IOTLAB_ARCH, win[0]):
                p += 1.0
        p /= 20
        if (p < 0.1):
            print("Sent successfully with packet loss of {0}%".format(p*100))
            return True
        print("")
    return False

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory> [nodes]" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])
    if len(sys.argv) == 3:
        nodesStr = sys.argv[2]

os.chdir("examples/gnrc_networking")

print("Run task #02")

helper = IOTLABHelper.IOTLABHelper()

testbed = helper.startExperiment(IOTLAB_EXP_NAME, IOTLAB_EXP_DUR, IOTLAB_NODES, IOTLAB_SITE, IOTLAB_ARCH, nodesStr)
if testbed == None:
    sys.exit(1)

availableNodes = helper.probeForNodes()
print("Available nodes: {0}".format([v[0] for v in availableNodes]))

if not helper.configureIPAddresses("dead:beef::{0}", IOTLAB_ARCH, availableNodes):
    print("Error while configuring IP addresses")
    sys.exit(1)

sortedNodes = []
while len(availableNodes):
    node = availableNodes[0]
    sortedNodes.append(node)
    availableNodes.remove(availableNodes[0])
    sorted(availableNodes, key=lambda x: math.sqrt(math.pow(x[1]-node[1],2) + \
                                          math.pow(x[2]-node[2],2) + \
                                          math.pow(x[3]-node[3],2)))

print("order of nodes for ping test: {0}".format([v[0] for v in sortedNodes]))

if not testUDP(helper, sortedNodes, NODES):
    print("Error while communicating with UDP")
    sys.exit(1)
else:
    print("Successfully communicated with UDP over {0} hops".format(NODES - 1))

print("SUCCESS")
