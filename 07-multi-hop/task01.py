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
IFACE = 7
PINGCOUNT = 10
PINGPAYLOADSZ = 100
PINGDELAY = 10

nodesStr = None

def testPing(helper, nodes, hops):
    localIPFormat = "fe80::{0}"
    globalIPFormat = "dead:beef::{0}"

    for win in helper.window(sortedNodes, hops):
        print("window: {0}".format([v[0] for v in win]))
        helper.setNibRoutesInARow(win, IOTLAB_ARCH, IFACE, globalIPFormat)
        if helper.ping(globalIPFormat.format(format(win[-1][0], 'x')), IOTLAB_ARCH, win[0],
                PINGCOUNT, PINGPAYLOADSZ, PINGDELAY):
            return True
        print("")
    return False

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])
    if len(sys.argv) == 3:
        nodesStr = sys.argv[2]

os.chdir("examples/gnrc_networking")

print("Run task #01")

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
    availableNodes.sort(key=lambda x: (math.pow(x[1]-node[1],2) +
                                       math.pow(x[2]-node[2],2) +
                                       math.pow(x[3]-node[3],2)))

print("order of nodes for ping test: {0}".format([v[0] for v in sortedNodes]))

if not testPing(helper, sortedNodes, NODES):
    print("Error while pinging")
    sys.exit(1)
else:
    print("Successfully pinged with {0} hops".format(NODES - 1))

print("SUCCESS")
