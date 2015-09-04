#!/usr/bin/env python

import pexpect
import os
import sys
import time
import random
from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError
import shlex

IOTLAB_ARCH = "m3"
IOTLAB_SITE = "grenoble"
IOTLAB_EXP_NAME = "RIOT_EXP_RPL_TEST"
IOTLAB_EXP_DUR = 3

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("examples/gnrc_networking")

print("Run task #03")

iotlabrc = os.path.expanduser('~') + os.path.sep + ".iotlabrc"
user_cmd = "cut -f1 -d: " + iotlabrc
user = check_output(shlex.split(user_cmd), universal_newlines=True).rstrip()
print("Authenticated as user: %s" % user)

while True:
    try:
        nodes = sorted(random.sample(range(358), 20))
        print("Start Experiment with nodes: %s" % nodes)
        exp_cmd = "experiment-cli submit -n {0} -d {1} -l {2},{3},{4}".format(IOTLAB_EXP_NAME,
                    IOTLAB_EXP_DUR, IOTLAB_SITE, IOTLAB_ARCH, "+".join(str(v) for v in nodes))
        expId = check_output(shlex.split(exp_cmd), universal_newlines=True).rstrip() \
                .split("\n")[1].split(": ")[1]
        break
    except CalledProcessError as err:
        print(err.output)
print("Experiment started with ID {0}".format(expId))
wait_cmd = "experiment-cli wait -i {0}".format(expId)
call(shlex.split(wait_cmd))

"""
TODO
* Connect to testbed
  socat tcp-listen:20000,fork,reuseaddr exec:'ssh <login>@grenoble.iot-lab.info "serial_aggregator -i <exp_id>"'
* Check fib of all nodes and retrieve longest path
  Should be > 2
* ping longest path
"""
print("SUCCESS")
