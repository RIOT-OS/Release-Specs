#!/usr/bin/env python

import pexpect
import os
import sys
import time

TESTBOARD = "native"

if len(sys.argv) < 2:
    print("Usage: %s <RIOT directory>" % (sys.argv[0]))
    sys.exit(1)
else:
    os.chdir(sys.argv[1])

os.chdir("tests/unittests")
os.environ['BOARD'] = TESTBOARD

print("Run task #03")
tests = os.listdir(".")
for t in tests:
    if t.startswith("tests-"):
        child = pexpect.spawn("make -B clean %s term" % t)
        try:
            child.expect("OK ")
        except pexpect.EOF:
            print("!!! Unittest %s failed" % t)
            sys.exit(1)


print("SUCCESS")
