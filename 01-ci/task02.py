#!/usr/bin/env python3

import os
import sys
import subprocess

TESTBOARD = "native"

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("tests/unittests")
os.environ['BOARD'] = TESTBOARD

print("Run task #02")
try:
    subprocess.check_call(["make", "-B", "clean", "all", "test"])
except subprocess.CalledProcessError:
    print("!!! Unittests failed")
    sys.exit(1)

print("SUCCESS")
