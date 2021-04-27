RIOT Release Specs
==================

This repository contains specifications and corresponding tests that have to be
fulfilled before a new RIOT release can be tagged.


Procedures
----------

Each RIOT release is accompanied by a set of release specifications, that have
to be passed before each RIOT release. The current master of this repository
contains the specs, that are applicable for the next release. So if we are in
feature freeze before a release, the release can only be tagged once all specs
that are in master of this repo are passed.

For traceability of past releases, a branch and a tag with the RIOT release name
is created on the day of the RIOT release. This way it is always clear, which
set of specs has been passed for specific release.


Specifications
--------------

### Structure

Each specification resides in it's own folder. Inside the folder you can find
a markdown file, that describes the specification and it's tasks in detail.
Optionally there are can be a number of test scripts and test applications for
each task.

A specification folder might look like the following:
```
/04-short-description
  | - spec-04.md
  | - test-04.01.py     -> test script for spec 04, task 01
  | - test-04.02.py
  | - test-04.03/       -> folder containing a specific RIOT test application
  |     | - main.c
  |     | - Makefile
  | - test-04.03.sh     -> some script making use of the test-04.03 application
  | - ....
/05-some-other-spec
  | - spec-05.md
  ...
/README.md
```

### Specs document

The release specifications are descriptions of test-cases and certain other
criteria that have to be tested/applied before each RIOT release. Each
specification contains a description of it's goal as well as a number of tasks
that have to be carried out (as much automated as possible).

Each tasks is to be written in the style of a test-case. This means, that the
following information must be given for each task:
- pre-requisites (e.g. RIOT application used, hardware used, network topology, )
- descriptions of how to exactly carry out the task (step-by-step if possible)
- a precise list of passing/failing criteria, so that there is no doubt if a
  task was successful or not

#### Missing a test or wondering why it got replaced?

The table in [REPLACED.md] documents for which release tests got deprecated and when
they are to be replaced and by what.

### Test scripts and applications

Each release specification should be accompanied by supporting scripts (and RIOT
applications if needed), that enable to execute it's tasks to the highest degree
of automation possible. The long-term goal is the complete automated execution
of all tasks, though there might be some cases where this is not achievable...

[REPLACED.md]: ./REPLACED.md

Tracking
--------

**TODO: verify if feasible of find other means to track the state**

The release spec repository also contains a tracking document (`results.md`),
which contains for each release candidate a full list of tasks that have to be
run, including the results, the exact RIOT commit the task was run with and the
date when  this was done.

This document serves (i) as a tracking document during the feature freeze phase
of a new release and (ii) as a back-reference, so we can trace which tasks have
been run for old releases.

The document `results.md` should have the following format:
```
...

215.12-RC2          -> same name as the tag in RIOT
----------

#### 01-ci          -> name of spec
task-01.01   2015-09-04   69aca17db6341f0f5acf683092af532b6eab6c53   success
task-01.02   2015-09-04   69aca17db6341f0f5acf683092af532b6eab6c53   fail
#### 02-tests
task-02.01   2015-09-03   69aca17db6341f0f5acf683092af532b6eab6c53   success
task-02.02   2015-09-04   69aca17db6341f0f5acf683092af532b6eab6c53   success
...

2015.12-RC1
-----------

task-01.01   2015-09-04   667ad24c557dd02b18a298ce50fc49b4a3c46269   fail
task-01.02   2015-09-04   667ad24c557dd02b18a298ce50fc49b4a3c46269   fail
#### 02-tests
task-02.01   2015-09-03   2eb21d8f9694146deca8c69cbc4a82acd62d395f   success
task-02.02   2015-09-04   2eb21d8f9694146deca8c69cbc4a82acd62d395f   success
#### ...
...

```

`pytest` runner
---------------

Many of the specs have python script to run the tests automatically. By default
experiments will be launched on [IoT-LAB saclay site] for tests that require
non-`native` boards. The saclay site was chosen since it has most of the
non-`native` boards used in the release-specs. Tests running on `native` will
always be run locally on the executing machine.  Non-`native` can also be ran
locally as long as the required `BOARD`s are available (see
[local requirements](#local-requirements)).

### Requirements

To use [pytest] you need to install the [`riotctrl`][riotctrl] and
[`iotlabcli`][iotlabcli] python packages:

```sh
pip install -r requirements.txt
```

Furthermore the `PYTHONPATH` needs to include the `pythonlibs` of RIOT:

```sh
export PYTHONPATH=${RIOTBASE}/dist/pythonlibs:${PYTHONPATH}
```

The environment variable `RIOTBASE` must be set to *absolute path* of the
version of RIOT under test. E.g.

```
export RIOTBASE=$(readlink -f ../RIOT)
```

Some tests on the `native` platform need a certain number of TAP interfaces in a
bridge or otherwise will be skipped. The most number of TAP interfaces to date
is required for 3.5 "ICMPv6 stress test on native (neighbor cache
stress)" (11 TAP interfaces) so to not skip that, all of them should be bridged.

```sh
sudo ${RIOTBASE}/dist/tools/tapsetup/tapsetup -c 11
```

#### Iot-LAB Requirements

The site on which to run the experiments can be changed by setting the
`IOTLAB_SITE` environment variable.

Make sure you can access the testbed frontend via SSH without providing a
password, either by generating a dedicated key pair without password

```sh
ssh-keygen
```

and adding that to your SSH config

```
Host *.iot-lab.info
    IdentityFile <generated private key>
```

or by configuring a dedicated `ssh-agent` (you might already have one provided
by your OS, check with `env | grep SSH_AUTH_SOCK`)

```sh
eval $(ssh-agent)
ssh-add
```

#### The Things Network Requirements

To be able to run the automatic tests in spec [11-lorawan] a valid TTN account
is required, and an application needs to be created with a device configure to
do `OTAA` and another configured to do `ABP`.

- [Create a TTN account]
- [Add an application]. Take note of:
  - Application ID as `TTN_APP_ID`
- [Register your device], one for `ABP` and a second for `OTAA`. Take note of:
  - ABP device ID as `TTN_DEV_ID_ABP`
  - OTAA device ID as `TTN_DEV_ID`
- Personalize a first device for OTAA (this is the default configuration).
  Take note of:
  - Device EUI as `DEVEUI`
  - Application EUI as `APPEUI`
  - App Key as `APPKEY`
- [Personalize device for ABP] and disable **Frame counter checks** to avoid
  having to reset the frame counters before every test run. Take note of:
  - Device Address as `DEVADDR`
  - Network Session Key as `NWKSKEY`
  - App Session Key as `APPSKEY`
- [Add an access key] to be able to use the MQTT API, the key must at least have
  access to `messages`. Take note of:
  - Access Key as `TTN_DL_KEY`

The listed variables need to be set in the environment.

[11-lorawan]: 11-lorawan/test_spec11.py
[Create a TTN account]: https://www.thethingsnetwork.org/docs/devices/node/quick-start/#create-an-account
[Add an application]: https://www.thethingsnetwork.org/docs/applications/add/
[Register your device]: https://www.thethingsnetwork.org/docs/devices/node/quick-start/#register-your-device
[Personalize device for ABP]: https://www.thethingsnetwork.org/docs/devices/registration/#personalize-device-for-abp
[Add an access key]: https://www.thethingsnetwork.org/docs/applications/mqtt/quick-start/index.html#credentials

#### Local Requirements

To be able to run tests locally the following requirements must be fulfilled:

- udev rules mapping every `BOARD` to a specific `PORT`, e.g.: `/dev/tty${BOARD}`.
- `makefile` included in `RIOT_MAKEFILES_GLOBAL_PRE` that sets `DEBUG_ADAPTER_ID`
  and `PORT` for each `BOARD`.

See [multiple boards udev] for a detailed walkthrough.

##### Limitations

- Currently only tests that run on different `BOARD`s will work out of the box,
  it would currently require setting an additional variable to identify each
  `BOARD`, see [multiple boards udev].

Future work could integrate a yml file that holds the configuration, [rjl] might
be a good reference.

### Usage

```
usage: pytest [--boards] [--hide-output] [--local] [--non-RC] [--self-test]
              [--log-file-fmt=[LOG_FILE_FMT]]

optional arguments:
  --boards              String list of boards to use for the test, can be
                        IOTLAB_NODE or RIOT BOARDs.
  --hide-output         Do not log output from nodes
  --local               Use local boards, default=False (will use IoT-LAB unless
                        all boards are native)
  --non-RC              Runs test even if RIOT version under test is not an RC
  --self-test           Tests the testutils rather than running the release
                        tests
  --log-file-fmt=[LOG_FILE_FMT]
                        Format for the log file name. The available variables
                        are: `module`: The module (=specXX) of the test,
                        `function`: The function (=taskXX) of the test, `node`:
                        Name of the node (on IoT-LAB the URL of the node,
                        locally board name + port), `time`: UNIX timestamp at
                        creation time. If the provided argument is an empty
                        string the format will be
                        '{module}-{function}-{node}-{time}.log' and stored in
                        the current work directory
```

Running `tox` will do most of that for you

```sh
tox
```

Want to see what's going on? Run

```sh
tox -- --capture=tee-sys
```

To run only local tests, run

```sh
tox -- --local
```

To run only tests that require root permissions, run

```sh
sudo RIOTBASE=${RIOTBASE} tox -- -m sudo_only
```

To run only a specific task you can use the `-k` option of `pytest`. It uses a
simple logical syntax for pattern matching so e.g.

```sh
tox -- -k "spec03 and (task01 or task05)"
```

will run task 1 and 5 of spec 3. The `-k` option can be used multiple times.
The expressions will be AND'd e.g.

```sh
tox -- -k spec03 -k "task01 or task05"
```

is identical to the first example.

##### Using an env file to keep persistent environment variables

Most tests require a set of user specific environment variable (path to
RIOTBASE, LoRaWAN keys, etc). In order to keep these variables persistent, a
.devdata.env file can be place in the root directory. For that, please make
a copy of ".devdata.env.sample" and modify accordingly:

```sh
cp .devdata.env.sample .devdata.env
```

[pytest]: https://pytest.org
[riotctrl]: https://pypi.org/project/riotctrl/
[IoT-LAB saclay site]: https://www.iot-lab.info/deployment/saclay/
[multiple boards udev]: http://riot-os.org/api/advanced-build-system-tricks.html#multiple-boards-udev
[rjl]: https://github.com/haukepetersen/rjl
