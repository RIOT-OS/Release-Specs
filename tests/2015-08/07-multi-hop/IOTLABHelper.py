#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Cenk Gündoğan <cnkgndgn@gmail.com>
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import random
import json
import pexpect
import os
import re
import time
from subprocess import call
from subprocess import check_output
import shlex
from itertools import groupby, count, islice
from operator import itemgetter
import getpass

class IOTLABHelper:
    def __init__(self):
        self.randomNodes = []
        self.testbed = None

    def __getLivingNodesFromTestbed(self, site, nodeType):
        nodesStr = check_output(shlex.split("experiment-cli info -li"), universal_newlines=True)
        nodesJSON = json.loads(nodesStr)['items']
        for siteJSON in nodesJSON:
            if site not in siteJSON:
                continue
            return siteJSON[site][nodeType]['Alive']
        return []

    def __getPhysicalLocation(self, nodes, site, nodeType):
        nodesWithPos = list()
        nodesStr = check_output(shlex.split("experiment-cli info -l --site {0}".format(site)), \
                                universal_newlines=True)
        nodesJSON = json.loads(nodesStr)['items']
        for node in nodesJSON:
            for nodeId in nodes:
                if "{0}-{1}.".format(nodeType, nodeId) in node['network_address']:
                    nodesWithPos.append(tuple((nodeId, float(node['x']), float(node['y']), \
                                               float(node['z']))))
                    break
        return nodesWithPos


    def __extractNodes(self, inputNodes):
        result = []

        for n in inputNodes.split("+"):
            spl = n.split("-")
            result += list(range(int(spl[0]), int(spl[1]) + 1)) if len(spl) > 1 else [int(n)]

        return sorted(result)

    def __compressNodes(self, inputNodes):
        return '+'.join(self.__as_range(g) for _, g in \
                        groupby([inputNode[0] for inputNode in inputNodes], \
                                key = lambda x, c = count(): x - next(c)))

    def __as_range(self, iterable):
        elem = list(iterable)
        return '{0}-{1}'.format(elem[0], elem[-1]) if len(elem) > 1 else '{0}'.format(elem[0])

    def getRandomTestbedNodes(self, sampleSize, site='grenoble', nodeType='m3'):
        livingNodes = self.__getLivingNodesFromTestbed(site, nodeType)
        nodes = self.__extractNodes(livingNodes)

        if sampleSize > len(nodes):
            print("Requested sample size must not exceed the number of distinct nodes")
            return "";

        randomNodes = [ nodes[i] for i in sorted(random.sample(range(len(nodes)), sampleSize)) ]
        return sorted(randomNodes)

    def startExperiment(self, expName, expDur, nodesNum, site, nodesType, nodes):
        iotlabrc = os.path.expanduser('~') + os.path.sep + ".iotlabrc"
        user = check_output(shlex.split("cut -f1 -d: " + iotlabrc), universal_newlines=True).rstrip()
        print("Authenticated as user: {0}".format(user))
        
        if nodes:
            nodes = self.__extractNodes(nodes)
            nodes = self.__getPhysicalLocation(nodes, site, nodesType)
            self.randomNodes = sorted(nodes, key=lambda node: node[0])
        else:
            randomNodes = self.getRandomTestbedNodes(nodesNum, site, nodesType)
            randomNodes = self.__getPhysicalLocation(randomNodes, site, nodesType)
            self.randomNodes = sorted(randomNodes, key=lambda node: node[0])

        nodesStr = self.__compressNodes(self.randomNodes)
        print("Starting experiment with nodes: {0}".format(nodesStr))
        
        exp_cmd = "make iotlab-exp -I ../../dist/testbed-support IOTLAB_USER={0} IOTLAB_EXP_NAME={1} " \
                  "IOTLAB_DURATION={2} BOARD=iotlab-m3 IOTLAB_PHY_NODES={3}" \
                  .format(user, expName, expDur, nodesStr)
        make = pexpect.run(exp_cmd, timeout=600)
        
        m = re.search('Waiting that experiment ([0-9]+) gets in state Running', make.decode())
        if m and m.group(1):
            expId = m.group(1)
        else:
            print("Experiment id could not be parsed")
            return None
        print("Experiment with id {0} started".format(expId))
        
        self.testbed = self.startAggregator(user, site, expId)
        print("Aggregator started")

        return self.testbed

    def startAggregator(self, user, site, expId):
        child = pexpect.spawn('ssh {0}@{1}.iot-lab.info -t "serial_aggregator -i {2}"' \
                              .format(user, site, expId), maxread=1)
        if child.expect([pexpect.TIMEOUT, "[pP]ass"], timeout=2) != 0:
                passw = getpass.getpass('Password: ')
                child.sendline(passw)
        time.sleep(2)
        return child

    def probeForNodes(self):
        self.testbed.sendline("invalid")
        nodes = set()
        cpl = self.testbed.compile_pattern_list([pexpect.TIMEOUT, "[0-9]+\.[0-9]+;.*?-([0-9]+);(?!Connection closed).*\n"])
        while self.testbed.expect_list(cpl, timeout=1) != 0:
            nodes.add([v for v in self.randomNodes if v[0] == int(self.testbed.match.group(1))][0])
        return sorted(nodes, key=lambda node: node[0])

    def setIPAddress(self, nodeType, nodeId, iface, ip):
        self.testbed.sendline("{0}-{1};ifconfig {2} add {3}".format(nodeType, nodeId, iface, ip))
        if self.testbed.expect([pexpect.TIMEOUT, "success"], timeout=1) != 0:
            return True
        print(self.testbed.before)
        return False
     
    def configureIPAddresses(self, ipFormat, nodeType, nodes):
        ret = True
        for node in nodes:
            ip = ipFormat.format((format(node[0], 'x')))
            print("Setting IP ({0}) for node {1}-{2} ... ".format(ip, nodeType, node[0]), end="")
            if not self.setIPAddress(nodeType, node[0], 7, ip):
                ret = False
                print("failed")
            else:
                print("success")
        return ret

    def setFibRoute(self, nodeType, nodeId, dst, nextHop):
        self.testbed.sendline("{0}-{1};fibroute add {2} via {3}".format(nodeType, nodeId, dst, nextHop))
        if self.testbed.expect([pexpect.TIMEOUT, "Please enter"], timeout=0.3) == 0:
            return True
        print(self.testbed.before)
        return False

    def setFibRoutesInARow(self, nodes, nodeType, localIPFormat, globalIPFormat):
        ret = True
        source = nodes[0]
        dest = nodes[-1]
        globalIPDest = globalIPFormat.format(format(dest[0], 'x'))

        readahead = iter(nodes)
        next(readahead)
        for a, b in zip(nodes, readahead):
            localIPA = localIPFormat.format(format(a[0], 'x'))
            localIPB = localIPFormat.format(format(b[0], 'x'))
            print("Setting route {0} via {1} for {2}-{3} ..." \
                  .format(globalIPDest, localIPB, nodeType, a[0]), end="")
            if not self.setFibRoute(nodeType, a[0], globalIPDest, localIPB):
                ret = False
                print("failed")
            else:
                print("success")

            print("Setting route {0} via {1} for {2}-{3} ... " \
                  .format("::", localIPA, nodeType, b[0]), end="")
            if not self.setFibRoute(nodeType, b[0], "::", localIPA):
                ret = False
                print("failed")
            else:
                print("success")

    def window(self, seq, n):
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def ping(self, ip, nodeType, node):
        print("Pinging ({0}) for node {1}-{2} ... ".format(ip, nodeType, node[0]), end="")
        self.testbed.sendline("{0}-{1};ping6 2 {2} 10 10".format(nodeType, node[0], ip))
        if self.testbed.expect([pexpect.TIMEOUT, " ([0-9][0-9]?)% packet loss"], timeout=20) != 0:
            print("success with {0}% packet loss".format(self.testbed.match.group(1).decode()))
            return True
        print("failed")
        return False

    def startUDPServer(self, node, nodeType, port):
        print("Starting UDP server on port {0} for {1}-{2} ... ". format(port, nodeType, node[0]), end="")
        self.testbed.sendline("{0}-{1};udp server start {2}".format(nodeType, node[0], port))
        if self.testbed.expect([pexpect.TIMEOUT, "Success"], timeout=0.5) != 0:
            print("success")
            return True
        print("failed")
        return False

    def stopUDPServer(self, node, nodeType, port):
        print("Stopping UDP server {0} for {1}-{2} ... ". format(nodeType, n[0]), end="")
        self.testbed.sendline("{0}-{1};udp server stop".format(nodeType, n[0]))
        if self.testbed.expect([pexpect.TIMEOUT, "Success"], timeout=0.5) != 0:
            print("success")
            return True
        print("failed")
        return False

    def sendUDP(self, src, dst, port, nodeType, node):
        print("Send UDP to {0} from node {1}-{2} ... ".format(dst, nodeType, node[0]), end="")
        self.testbed.sendline("{0}-{1};udp send {2} {3} test".format(nodeType, node[0], dst, port))
        if self.testbed.expect([pexpect.TIMEOUT, "source address: {0}".format(src)], timeout=1) != 0:
            print("success")
            return True
        print("failed")
        return False
