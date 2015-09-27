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

print("Run task #01")
child = pexpect.spawn("./dist/tools/compile_test/compile_test.py", timeout=3600)
try:
    child.expect("failed")
    print("!!! compile tests failed")
    sys.exit(1)
except pexpect.EOF:
    print("SUCCESS")
