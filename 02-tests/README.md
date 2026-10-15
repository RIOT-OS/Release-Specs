## Goal: Perform test applications on various platforms and check that they run as expected

### Usage

Firstly, run `dist/tools/tapsetup/tapsetup` if you want to test for `native`.
Then, run the
`dist/tools/compile_and_test_for_board/compile_and_test_for_board.py` script
with your test board connected.

See `dist/tools/compile_and_test_for_board/README.md` and script `--help`
for usage.

### CI support

The workflow [`test-on-iotlab`](https://github.com/RIOT-OS/RIOT/actions/workflows/test-on-iotlab.yml)
executes all tests on all boards listed below (except `native`), using nodes available at the IoT-Lab.


Task #01 - All tests on native
==============================
### Description

Execute all tests on native and check their output.

### Result

All tests succeed.

Task #02 - All tests on iotlab-m3
=================================
### Description

Execute all tests on iotlab-m3 node.

### Result

All tests succeed.

Task #03 - All tests on samr21-xpro
===================================
### Description

Execute all tests on samr21-xpro node.

### Result

All tests succeed.

Task #04 - All tests on nrf52840dk
==================================
### Description

Execute all tests on nrf52840dk node.

### Result

All tests succeed.

Task #05 - All tests on b-l072z-lrwan1
======================================
### Description

Execute all tests on b-l072z-lrwan1 node.

### Result

All tests succeed.

