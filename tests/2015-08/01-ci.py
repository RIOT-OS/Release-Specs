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

print("Run task #01")
child = pexpect.spawn("./dist/tools/compile_test/compile_test.py", timeout=3600)
try:
    child.expect("failed")
    print("!!! compile tests failed")
    sys.exit(1)
except pexpect.EOF:
    pass

os.chdir("tests/unittests")
print("Run task #02")
child = pexpect.spawn("make -B clean all term")
try:
    child.expect("OK ")
except pexpect.EOF:
    print("!!! Unittests failed")
    sys.exit(1)

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
