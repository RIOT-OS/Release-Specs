import os
import pexpect
import signal
import io
import subprocess


class Board:
    def __init__(self, cmd):
        self.logger = io.StringIO()
        self.pexpect = pexpect.spawnu(
                cmd, codec_errors='replace', timeout=30,
                logfile=self.logger)
        self.pexpect.setecho(False)

    def reboot(self):
        self.pexpect.sendline("reboot")
        self.pexpect.expect("RIOT")

    def stop(self):
        try:
            os.killpg(os.getpgid(self.pexpect.pid), signal.SIGKILL)
        except ProcessLookupError:
            print("Process already stopped")
        self.pexpect = None
        self.logger.close()
        self.logger = None


def bootstrap(board, env={}):
    env.update(os.environ)
    subprocess.check_call(["make", "BOARD={}".format(board), "clean", "all"], env=env)
