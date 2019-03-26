Summary
=======

These tests replicate a number of tests that are performed by Murdock. The
purpose of this is to check these tests build and run correctly on a range of user
platforms.

Task #01 - Compile test
=======================
### Description

Execute ./dist/tools/compile_test/compile_test.py

### Result

Everything builds as expected. No errors, no warnings.

Task #02 - Unittests on native
==============================
### Description

Run all unittests at once in native.

### Result

All tests run successfully. (Output says: "OK (xyz tests)"

Task #03 - Unittests on native separated
=======================================
### Description

Run all unittests separately in native.

### Result

All tests run successfully. (Output says: "OK (xyz tests)"

Task #04 - Unittests on iotlab-m3
=================================
### Description

Run all unittests at once on an iotlab-m3 node.

### Result

All tests run successfully. (Output says: "OK (xyz tests)"
