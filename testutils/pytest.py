"""
Helpers for pytest
"""

import os
import re
import subprocess

import pexpect.replwrap
import pytest

from .iotlab import IoTLABExperiment, DEFAULT_SITE, IOTLAB_DOMAIN


def list_from_string(list_str=None):
    """Get list of items from `list_str`

    >>> list_from_string(None)
    []
    >>> list_from_string("")
    []
    >>> list_from_string("  ")
    []
    >>> list_from_string("a")
    ['a']
    >>> list_from_string("a  ")
    ['a']
    >>> list_from_string("a b  c")
    ['a', 'b', 'c']
    """
    value = (list_str or '').split(' ')
    return [v for v in value if v]


def log_file_fmt(fmt_str=None):
    """Get defaulted format string

    >>> import os
    >>> log_file_fmt(None)
    >>> os.path.basename(log_file_fmt(''))
    '{module}-{function}-{node}-{time}.log'
    >>> log_file_fmt('foobar')
    'foobar'
    >>> log_file_fmt('{module}-{function}-{time}-{node}')
    '{module}-{function}-{time}-{node}'
    """
    if fmt_str is not None:
        if len(fmt_str) > 0:
            return fmt_str
        return os.path.join(os.getcwd(),
                            "{module}-{function}-{node}-{time}.log")
    return None


def check_ssh():
    user, _ = IoTLABExperiment.user_credentials()
    if user is None:
        return False
    spawn = pexpect.spawnu(f"ssh {user}@{DEFAULT_SITE}.{IOTLAB_DOMAIN} /bin/bash")
    spawn.sendline("echo $USER")
    return bool(spawn.expect([pexpect.TIMEOUT, f"{user}"],
                             timeout=5))


def check_sudo():
    sudo_only_mark = None
    if os.geteuid() != 0:
        sudo_only_mark = pytest.mark.skip(reason="Test needs sudo to run")
    return sudo_only_mark


def check_local(run_local):
    local_only_mark = None
    if not run_local:
        local_only_mark = pytest.mark.skip(reason="Test can't run on IoT-LAB")
    return local_only_mark


def check_credentials(run_local):
    iotlab_creds_mark = None
    if not run_local and not IoTLABExperiment.check_user_credentials():
        iotlab_creds_location = os.path.join(os.environ["HOME"], ".iotlabrc")
        iotlab_creds_mark = pytest.mark.skip(
            reason=f"Test requires IoT-LAB credentials in {iotlab_creds_location}. "
                   "Use `iotlab-auth` to create"
        )
    elif not run_local and not check_ssh():
        iotlab_creds_mark = pytest.mark.skip(
            reason="Can't access IoT-LAB front-end {DEFAULT_SITE}.{IOTLAB_DOMAIN} "
                   "via SSH. Use key without password or `ssh-agent`"
        )
    return iotlab_creds_mark


def check_rc(only_rc_allowed):
    rc_only_mark = None
    output = subprocess.check_output([
        "git", "-C", os.environ["RIOTBASE"], "log", "-1", "--oneline",
        "--decorate"
    ]).decode()
    is_rc = re.search(r"tag:\s\d{4}.\d{2}-RC\d+", output) is not None

    if only_rc_allowed and not is_rc:
        rc_only_mark = pytest.mark.skip(
            reason="RIOT version under test is not a release candidate"
        )
    return rc_only_mark


def get_required_envvar(envvar):
    """
    Returns the value of an environment variable. Raise RuntimeError otherwise.
    """
    try:
        return os.environ[envvar]
    except KeyError as err:
        raise RuntimeError(f"Missing {envvar} env variable") from err
