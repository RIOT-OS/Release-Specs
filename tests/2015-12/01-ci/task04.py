#!/usr/bin/env python

import pexpect
import os
import sys
import time

TESTBOARD = "iotlab-m3"

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("tests/unittests")

os.environ['BOARD'] = TESTBOARD 
print("Run task #04")
pexpect.run("make -B clean all")
child = pexpect.spawn("make flash")

try:
    child.expect("verified")
except pexpect.EOF:
    print("!!! Flashing %s failed" % TESTBOARD)
    sys.exit(1)

child = pexpect.spawn("make term")
time.sleep(1)
pexpect.run("make reset")
try:
    child.expect("OK ")
except pexpect.EOF:
    print("!!! Unittests on %s failed" % TESTBOARD)
    sys.exit(1)

print("SUCCESS")
