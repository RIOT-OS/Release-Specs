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
executes all automatic tests on all boards listed below (except `native`), using nodes available at the IoT-Lab.
Automatic tests on `native` are executed in the nightlies by Murdock.

Automatic tests are those where a Python script `01-run.py` exists in the application subfolder `tests`.
`tests-with-config` and `tests-as-root` are currently not automatically executed by the CI mentioned here.
However, they can be executed locally by setting, e.g., the following parameters for the
`compile_and_test_for_boards.py` script and replace `test` with
`test-as-root` or `test-with-config` respectively.

```
  --test-targets TEST_TARGETS
                        List of make targets to run test (default: test)
  --test-available-targets TEST_AVAILABLE_TARGETS
                        List of make targets to know if a test is present (default: test/available)
```

**Make sure**, that for the `test-with-config` test target the configurations that the `test-with-config`
expects in each respective test, are set accordingly (check each test individually for that).
`--clean-after` helps to clean-up sudo-built files after the test.


Task #01 - All tests on native
==============================
### Description

Execute all tests on native and check their output.

### Result

All tests succeed.

Task #02 - Subset of tests on iotlab-m3
=======================================
### Description

Execute all automatic tests on iotlab-m3 node.

### Result

All tests succeed.

Task #03 - Subset of tests on samr21-xpro
=========================================
### Description

Execute all automatic tests on samr21-xpro node.

### Result

All tests succeed.

Task #04 - Subset of tests on nrf52840dk
========================================
### Description

Execute all automatic tests on nrf52840dk node.

### Result

All tests succeed.

Task #05 - Subset of tests on b-l072z-lrwan1
============================================
### Description

Execute all automatic tests on b-l072z-lrwan1 node.

### Result

All tests succeed.

