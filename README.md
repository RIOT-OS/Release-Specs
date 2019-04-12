RIOT Release Specifications
===========================

This repository contains the criteria for a release, specifically the release
acceptance tests.

The tests are performed repeatedly on a series of release candidates, with
iterative bugfixing. The testing for each release candidate is tracked on an
issue in this repository. All tests passing is the goal, but if this is not
feasible in any one release cycle due to the number of known bugs, a judgement
call must be made by the engineers as to what is satisfactory. The known issues
are then recorded in release-notes.txt in the main RIOT repository.

For further details of the release process, see the [release management wiki
page](https://github.com/RIOT-OS/RIOT/wiki/%5Bdraft%5D-Managing-a-Release).

The scope, and automation, of the tests should be being improved continuously.

Test summary
------------

The tests are listed below. Each "test" consists of a number of "tasks".

| Test name                     | Description                                                      |
|-------------------------------|------------------------------------------------------------------|
| 01-ci                         | Compile, and run unit tests, on a range of development platforms |
| 02-tests                      | Run other automatable tests on a selection of boards             |
| 03-single-hop-ipv6-icmp       | Single hop IPv6 ping tests between native instances              |
| 04-single-hop-6lowpan-icmp    | Single-hop 6LoWPAN ping tests between nodes                      |
| 05-single-hop-route           | Static routing of ICMPv6 packets over a single hop               |
| 06-single-hop-udp             | Single-hop UDP connectivity over IPv6                            |
| 07-multi-hop                  | Multi-hop connectivity over IPv6                                 |
| 08-interop                    | Interoperability of gnrc with different implementations          |
| 09-coap                       | Send and receive of typical CoAP messages                        |
| 10-icmpv6-error               | ICMP error handling                                              |
| 11-lorawan                    | LoRaWAN networking                                               |
| 99-compile-and-test-one-board | Extension - Test 02 for as many extra boards as possible         |

Directory structure
-------------------

A specification's directory must contain a markdown document specifying the tests
to perform and the status of automation of those tests. Additionally, it might
contain Python scripts which automate the tests, and/or RIOT test applications
which implement the tests.

```
/04-short-description
  | - spec-04.md
  | - test-04.01.py     -> test script for spec 04, task 01
  | - test-04.02.py
  | - test-04.03/       -> folder containing a specific RIOT test application
  |     | - main.c
  |     | - Makefile
  | - test-04.03.sh     -> some script making use of the test-04.03 application
  | - ...
/05-some-other-spec
  | - spec-05.md
  ...
/README.md
```

The following information should be given in the markdown document, for each task:

- pre-requisites (e.g. RIOT application used, hardware used, network topology, ... ).
- Unambiguous descriptions of exactly how to carry out the task (step-by-step
  if possible).
- a precise description of pass/fail criteria.
