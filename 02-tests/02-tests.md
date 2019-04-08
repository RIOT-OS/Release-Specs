Summary
=======

These tests compile all applications and tests, and automatically run all tests
that only require the board, for a selection of individual boards.

### Usage

Run 02 `compile_and_test_for_board.py` script with your test board connected.

    ./compile_and_test_for_board.py path_to_riot_directory board_name [results]

It prints the summary with results files relative to `results_dir/board` to have
a github friendly output.

Failures and all tests output are saved in files.
They can be checked with:

    find results/ -name '*.failed'
    find results/ -name 'test.success'


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
