import os
import logging
import subprocess


logger = logging.getLogger(__name__)


class GitError(subprocess.CalledProcessError):
    pass


class Git:
    def __init__(self, root='.', quiet=True):
        self._root = root
        self._quiet = quiet

    def __repr__(self):
        return f"<{type(self).__name__}: {self._root}>"

    @staticmethod
    def _cmd(cmd, quiet=True):
        stderr = subprocess.DEVNULL if quiet else None
        try:
            return subprocess.check_output(cmd, stderr=stderr).decode()
        except subprocess.CalledProcessError as exc:
            raise GitError(exc.returncode, exc.cmd, exc.output, exc.stderr) from exc

    def exists(self):
        return os.path.isdir(self._root)

    def staging_changed(self):
        output = self.diff('--cached')
        return output.strip() != ''

    def cmd(self, subcmd, *args):
        cmd = ['git', '-C', self._root, subcmd]
        cmd.extend(args)
        return self._cmd(cmd, quiet=self._quiet)

    @classmethod
    def clone(cls, url, root, *args, quiet=True):
        cmd = ['git', 'clone']
        cmd.extend(args)
        cmd.extend([url, root])
        output = cls._cmd(cmd, quiet=quiet)
        logger.info(output)
        return Git(root, quiet=quiet)

    @property
    def repodir(self):
        return self._root

    @property
    def head_sha(self):
        return self.cmd('rev-parse', 'HEAD').strip()

    def diff(self, *args):
        return self.cmd('diff', *args)

    def add(self, *args):
        return self.cmd('add', *args)

    def commit(self, *args):
        return self.cmd('commit', *args)

    def log(self, *args):
        return self.cmd('log', *args)

    def pull(self, *args):
        return self.cmd('pull', *args)

    def push(self, *args):
        return self.cmd('push', *args)
