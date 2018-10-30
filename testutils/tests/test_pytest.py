import pytest

import testutils.pytest


class MockSpawn():
    expect_ret = None

    # pylint: disable=W0613
    def __init__(self, cmd, *args, **kwargs):
        self.cmd = cmd

    # pylint: disable=W0613
    def sendline(self, *args, **kwargs):
        pass

    # pylint: disable=W0613
    def expect(self, *args, **kwargs):
        return self.expect_ret


@pytest.mark.parametrize(
    "iotlab_creds,expect_ret,expect_func",
    [(("test", None), 1, lambda x: x),
     (("test", None), 0, lambda x: not x),
     ((None, None), 0, lambda x: not x),
     ((None, None), 1, lambda x: not x)]
)
def test_check_ssh_creds(monkeypatch, iotlab_creds, expect_ret, expect_func):
    monkeypatch.setattr(testutils.pytest.IoTLABExperiment, "user_credentials",
                        lambda: iotlab_creds)
    monkeypatch.setattr(testutils.pytest.pexpect, "spawnu", MockSpawn)
    MockSpawn.expect_ret = expect_ret
    assert expect_func(testutils.pytest.check_ssh())


@pytest.mark.parametrize(
    "iotlab_creds,expect_ret,run_local,expect_func",
    [(("test", None), 1, False, lambda x: not x),
     (("test", None), 0, False, lambda x: x),
     ((None, None), 0, False, lambda x: x),
     ((None, None), 1, False, lambda x: x),
     ((None, None), 0, True, lambda x: not x),
     (("test", None), 1, True, lambda x: not x)]
)
def test_check_credentials(monkeypatch, iotlab_creds, expect_ret, expect_func,
                           run_local):
    monkeypatch.setattr(testutils.pytest.IoTLABExperiment, "user_credentials",
                        lambda: iotlab_creds)
    monkeypatch.setattr(testutils.pytest.pexpect, "spawnu", MockSpawn)
    MockSpawn.expect_ret = expect_ret
    assert expect_func(testutils.pytest.check_credentials(run_local))


@pytest.mark.parametrize(
    "output,only_rc_allowed,expect_func",
    [(b"foobar", False, lambda x: not x),
     (b"foobar", True, lambda x: x),
     (b"tag: 2042.06-RC13", True, lambda x: not x),
     (b"tag: 2042.06-RC13", False, lambda x: not x)]
)
def test_check_rc(monkeypatch, output, only_rc_allowed, expect_func):
    monkeypatch.setattr(testutils.pytest.subprocess, "check_output",
                        lambda *args, **kwargs: output)
    assert expect_func(testutils.pytest.check_rc(only_rc_allowed))
