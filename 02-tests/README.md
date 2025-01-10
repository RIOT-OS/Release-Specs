## Goal: Perform test applications on various platforms and check that they run as expected

### Usage

Firstly, run `dist/tools/tapsetup/tapsetup` if you want to test for `native`.
Then, run the
`dist/tools/compile_and_test_for_board/compile_and_test_for_board.py` script
with your test board connected.

See `dist/tools/compile_and_test_for_board/README.md` and script `--help`
for usage.


Task #01 - All tests on native
==============================
### Description

Execute all tests on native and check their output.

### Result

All tests succeed.

Task #02 - Subset of tests on iotlab-m3
=======================================
### Description

Perform a subset of tests on iotlab-m3 node.

### Result

All tests succeed.

Task #03 - Subset of tests on samr21-xpro
=========================================
### Description

Perform a subset of tests (!= subset from Task #02) on samr21-xpro node.

### Result

All tests succeed.

Task #04 - Subset of tests on native64
=======================================
### Description

Perform a subset of tests on native64 and check their output.

### Result

All tests succeed.
