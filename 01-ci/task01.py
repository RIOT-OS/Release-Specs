#!/usr/bin/env python3

"""Compile all tests and examples for all boards.

Usage
-----

```
usage: task01.py [-h] [--stop] riot_directory

compile all tests and examples for all boards

positional arguments:
  riot_directory

optional arguments:
  -h, --help      show this help message and exit
  --stop          Stop test on first error
```
"""

import os
import sys
import argparse

import pexpect


PARSER = argparse.ArgumentParser(
    description='Compile all tests and examples for all boards')
PARSER.add_argument('riot_directory')
PARSER.add_argument('--stop', action='store_true', default=False,
                    help='Stop test on first error')


def _run_compile_tests(riot_directory, stop=False):
    """Run compile tests and return the number of "failed"."""
    os.chdir(riot_directory)

    child = pexpect.spawnu("./dist/tools/compile_test/compile_test.py",
                           timeout=None, logfile=sys.stdout)
    errors = 0
    try:
        while True:
            child.expect("failed")
            errors += 1
            if stop:
                break
    except pexpect.EOF:
        pass

    return errors


def main():
    """Execute compilation tests."""
    args = PARSER.parse_args()

    print("Run task #01")

    errors = _run_compile_tests(args.riot_directory, args.stop)

    if errors:
        print("!!! %u compile tests failed" % errors)
        exit(errors)

    print("SUCCESS")


if __name__ == '__main__':
    main()
