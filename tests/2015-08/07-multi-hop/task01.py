#!/usr/bin/env python

import pexpect
import os
import sys
import time
import IOTLABHelper
import itertools
import math

IOTLAB_ARCH = "m3"
IOTLAB_SITE = "grenoble"
IOTLAB_EXP_NAME = "RIOT_EXP_PING_TEST"
IOTLAB_EXP_DUR = 5
IOTLAB_NODES = 15

def configureRoutes(nodes):
    sortedNodes = []
    while len(nodes):
        node = nodes[0]
        sortedNodes.append(node)
        nodes.remove(nodes[0])
        sorted(nodes, key=lambda x: math.sqrt(math.pow(x[1]-node[1],2) + \
                                              math.pow(x[2]-node[2],2) + \
                                              math.pow(x[3]-node[3],2)))

    print("order of nodes for pinging test: {0}".format([v[0] for v in sortedNodes]))

    readahead1 = iter(sortedNodes)
    next(readahead1)
    readahead2 = iter(sortedNodes)
    next(readahead2)
    next(readahead2)
    readahead3 = iter(sortedNodes)
    next(readahead3)
    next(readahead3)
    next(readahead3)

    ret = True
    for nodeA, nodeB, nodeC, nodeD in zip(sortedNodes, readahead1, readahead2, readahead3):
        globalIPA = "dead:beef::{0}".format((format(nodeA[0], 'x')))
        localIPA = "fe80::{0}".format((format(nodeA[0], 'x')))
        globalIPB = "dead:beef::{0}".format((format(nodeB[0], 'x')))
        localIPB = "fe80::{0}".format((format(nodeB[0], 'x')))
        globalIPC = "dead:beef::{0}".format((format(nodeC[0], 'x')))
        localIPC = "fe80::{0}".format((format(nodeC[0], 'x')))
        globalIPD = "dead:beef::{0}".format((format(nodeD[0], 'x')))
        localIPD = "fe80::{0}".format((format(nodeD[0], 'x')))

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPB, localIPB, IOTLAB_ARCH, nodeA[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeA[0], globalIPB, localIPB):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPC, localIPB, IOTLAB_ARCH, nodeA[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeA[0], globalIPC, localIPB):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPD, localIPB, IOTLAB_ARCH, nodeA[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeA[0], globalIPD, localIPB):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format("::", localIPA, IOTLAB_ARCH, nodeB[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeB[0], "::", localIPA):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPC, localIPC, IOTLAB_ARCH, nodeB[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeB[0], globalIPC, localIPC):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPD, localIPC, IOTLAB_ARCH, nodeB[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeB[0], globalIPD, localIPC):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format("::", localIPB, IOTLAB_ARCH, nodeC[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeC[0], "::", localIPB):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format(globalIPD, localIPD, IOTLAB_ARCH, nodeC[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeC[0], globalIPD, localIPD):
            ret = False
            print("failed")
        else:
            print("success")

        print("Setting route {0} via {1} for {2}-{3} ... " \
              .format("::", localIPC, IOTLAB_ARCH, nodeD[0]), end="")
        if not helper.setFibRoute(IOTLAB_ARCH, nodeD[0], "::", localIPC):
            ret = False
            print("failed")
        else:
            print("success")

        if not helper.ping(globalIPD, IOTLAB_ARCH, nodeA):
            ret = False
        print("")
    return ret

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("examples/gnrc_networking")

print("Run task #01")

helper = IOTLABHelper.IOTLABHelper()

testbed = helper.startExperiment(IOTLAB_EXP_NAME, IOTLAB_EXP_DUR, IOTLAB_NODES, IOTLAB_SITE, IOTLAB_ARCH)
if testbed == None:
    sys.exit(1)

availableNodes = helper.probeForNodes()
print("Available nodes: {0}".format([v[0] for v in availableNodes]))

if not helper.configureIPAddresses("dead:beef::{0}", IOTLAB_ARCH, availableNodes):
    print("Error while configuring IP addresses")
    sys.exit(1)

if not configureRoutes(availableNodes):
    print("Error while configuring routes and pinging")
    sys.exit(1)

print("SUCCESS")
