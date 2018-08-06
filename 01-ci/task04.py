#!/usr/bin/env python3

import os
import sys
import subprocess

TESTBOARD = "iotlab-m3"

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("tests/unittests")

os.environ['BOARD'] = TESTBOARD

print("Run task #04")
subprocess.check_call(['make', '-B', 'clean', 'all'])

try:
    subprocess.check_call(['make', 'flash-only'])
except subprocess.CalledProcessError:
    print("!!! Flashing %s failed" % TESTBOARD)
    sys.exit(1)

try:
    subprocess.check_call(['make', 'test'])
except subprocess.CalledProcessError:
    print("!!! Unittests on %s failed" % TESTBOARD)
    sys.exit(1)

print("SUCCESS")
