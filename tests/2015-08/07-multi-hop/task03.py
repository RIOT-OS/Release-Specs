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
IOTLAB_EXP_DUR = 15
IOTLAB_NODES = 20
INSTANCE_ID = 155
nodesStr = None
ROOT_NODE_IDX = 3
IFACE = 7

def testPing(helper, nodes):
    prefix = "dead:beef::"

    print("rplnodes: {0}".format([(v[0][0],v[1]) for v in nodes]))
    ret = True
    for a, b in itertools.permutations(nodes, 2):
        ip = helper.findAddressByPrefix(IOTLAB_ARCH, b[0][0], IFACE, prefix)
        if ip is None:
            print("Could not find IP address of {0}-{1}. continue".format(IOTLAB_ARCH, b[0][0]))
            continue
        print("Ping [{0}-{1} -> {2}-{3}]".format(IOTLAB_ARCH, a[0][0], IOTLAB_ARCH, b[0][0]))
        if not helper.ping(ip, IOTLAB_ARCH, a[0]):
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

if not helper.configureIPAddresses("dead:beef::{0}", IOTLAB_ARCH, [availableNodes[ROOT_NODE_IDX]]):
    print("Error while configuring IP addresses")
    testbed.sendline("reboot")
    testbed.kill(0)
    sys.exit(1)

for n in availableNodes:
    if not helper.rplInit(n, IOTLAB_ARCH, IFACE):
        print("Error initializing RPL")
        testbed.sendline("reboot")
        testbed.kill(0)
        sys.exit(1)

helper.rplRoot(availableNodes[ROOT_NODE_IDX], IOTLAB_ARCH, INSTANCE_ID, "dead:beef::{0}".format(format(availableNodes[ROOT_NODE_IDX][0], 'x')))

print("Waiting for 30 seconds so that RPL can build the DODAG")
time.sleep(30)

rplNodes = helper.getRplNodes(INSTANCE_ID, "dead:beef::{0}".format(format(availableNodes[ROOT_NODE_IDX][0], 'x')), IOTLAB_ARCH)

if not testPing(helper, rplNodes):
    print("Error while pinging")
    testbed.sendline("reboot")
    testbed.kill(0)
    sys.exit(1)

testbed.sendline("reboot")
testbed.kill(0)
print("SUCCESS")
