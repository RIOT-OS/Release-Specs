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
IOTLAB_EXP_NAME = "RIOT_EXP_RPL_PING_TEST"
IOTLAB_EXP_DUR = 5
IOTLAB_NODES = 20
nodesStr = None

def testPing(helper, nodes):
    globalIPFormat = "dead:beef::{0}"

    ret = True
    print("rplNodes: {0}".format(nodes))
    for a, b in itertools.permutations(nodes, 2):
        print(a)
        print(b)
        if not helper.ping(globalIPFormat.format(format(b[0][0], 'x')), IOTLAB_ARCH, a[0]):
            ret = False
        print("")
    return ret

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])
    if len(sys.argv) == 3:
        nodesStr = sys.argv[2]

os.chdir("examples/gnrc_networking")

print("Run task #03")

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

rplNodes = helper.getRplNodes(1, "dead:beef::{0}".format(format(availableNodes[0][0], 'x')), IOTLAB_ARCH)

if not testPing(helper, rplNodes):
    print("Error while pinging")
    sys.exit(1)

print("SUCCESS")
