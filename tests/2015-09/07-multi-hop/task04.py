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
IOTLAB_EXP_DUR = 60
IOTLAB_NODES = 20
PORT = 1337
INSTANCE_ID = 155
nodesStr = None
UDP_NUMOF = 10
ROOT_NODE_IDX = 3
IFACE = 7
root = None

def printRouteValidation(helper, node, prefix):
    while True:
        print("{0} ".format(node), end="")
        parent = helper.getRplParent(IOTLAB_ARCH, node, IFACE)
        if parent is None:
            break
        if helper.hasDefaultRouteToParent(IOTLAB_ARCH, node, parent, IFACE):
            print("[YES]", end="")
        else:
            print("[NO]", end="")
        print(" => ", end="")
        if helper.hasDownwardRoute(IOTLAB_ARCH, parent, node, IFACE, prefix):
            print("[YES]", end="")
        else:
            print("[NO]", end="")
        print(" {0} | ".format(parent), end="")
        node = parent
    print("")

def checkNodes(helper, nodes, availableNodes, root):
    currentRplNodes = helper.getRplNodes(INSTANCE_ID, "dead:beef::{0}".format(format(root[0], 'x')), IOTLAB_ARCH)
    noRplNodesAnymore = [n[0][0] for n in nodes if n not in currentRplNodes]
    if len(noRplNodesAnymore) > 0:
        print("No RPL nodes anymore: {0}".format(noRplNodesAnymore))
    currentAvailableNodes = helper.probeForNodes()
    notAvailAnymore = [n[0] for n in availableNodes if n not in currentAvailableNodes]
    if len(notAvailAnymore) > 0:
        print("Nodes crashed: {0}".format(notAvailAnymore))

def testUDP(helper, nodes, availableNodes, root):
    prefix = "dead:beef::"

    print("rplnodes: {0}".format([(v[0][0],v[1]) for v in nodes]))
    for n in nodes:
        helper.startUDPServer(n[0], IOTLAB_ARCH, PORT)

    ret = True
    for a, b in itertools.permutations(nodes, 2):
        ipFrom = helper.findAddressByPrefix(IOTLAB_ARCH, a[0][0], IFACE, prefix)
        ipTo = helper.findAddressByPrefix(IOTLAB_ARCH, b[0][0], IFACE, prefix)
        print("Send UDP [{0}-{1} -> {2}-{3}]".format(IOTLAB_ARCH, a[0][0], IOTLAB_ARCH, b[0][0]))
        p = 0.0
        for i in range(UDP_NUMOF):
            if not helper.sendUDP(ipFrom, ipTo, PORT, IOTLAB_ARCH, a[0]):
                p += 1.0
        p /= UDP_NUMOF
        if (p < 0.1):
            print("Sent successfully with packet loss of {0}%".format(p*100))
        else:
            ret = False
        checkNodes(helper, nodes, availableNodes, root)
        printRouteValidation(helper, a[0][0], prefix)
        printRouteValidation(helper, b[0][0], prefix)
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

root = availableNodes[ROOT_NODE_IDX]

if not helper.configureIPAddresses("dead:beef::{0}", IOTLAB_ARCH, [root]):
    print("Error while configuring IP addresses")
    testbed.sendline("reboot")
    testbed.kill(0)
    sys.exit(1)

for n in availableNodes:
    if not helper.rplInit(n, IOTLAB_ARCH, 7):
        print("Error initializing RPL")
        testbed.sendline("reboot")
        testbed.kill(0)
        sys.exit(1)

helper.rplRoot(root, IOTLAB_ARCH, INSTANCE_ID, "dead:beef::{0}".format(format(root[0], 'x')))

print("Waiting for 30 seconds so that RPL can build the DODAG")
time.sleep(30)

rplNodes = helper.getRplNodes(INSTANCE_ID, "dead:beef::{0}".format(format(root[0], 'x')), IOTLAB_ARCH)

if not testUDP(helper, rplNodes, availableNodes, root):
    print("Error while communicating with UDP")
    testbed.sendline("reboot")
    testbed.kill(0)
    sys.exit(1)

testbed.sendline("reboot")
testbed.kill(0)
print("SUCCESS")
