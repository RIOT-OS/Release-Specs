## Goal: Maintainers run the test suit on additional boards

Task #01 - Run tests on different hardwares
===========================================

### Description

Can be done multiple times for different boards.

Compile all applications and run tests when available on a given board.
Run [`02-tests`][02-tests] procedure with your test board connected.

Please make the result files available to the release manager.

Note: For some boards there are weekly runs in the CI in [test-on-iotlab] and [test-on-ryot].

[02-tests]: ../02-tests
[test-on-iotlab]: https://github.com/RIOT-OS/RIOT/actions/workflows/test-on-iotlab.yml
[test-on-ryot]: https://github.com/RIOT-OS/RIOT/actions/workflows/test-on-ryot.yml
