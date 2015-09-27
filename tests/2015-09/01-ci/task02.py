#!/usr/bin/env python

import pexpect
import os
import sys
import time

TESTBOARD = "iot-lab_M3"

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("tests/unittests")
print("Run task #02")
child = pexpect.spawn("make -B clean all term")
try:
    child.expect("OK ")
except pexpect.EOF:
    print("!!! Unittests failed")
    sys.exit(1)

print("SUCCESS")
