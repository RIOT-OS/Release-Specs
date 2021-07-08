import re
import subprocess

import pytest

import testutils.git

# pylint: disable=redefined-outer-name


def config_repo(git):
    git.cmd('config', 'user.email', 'you@example.org')
    git.cmd('config', 'user.name', 'Your Name')


@pytest.fixture
def bare_repo(tmp_path):
    git = testutils.git.Git(tmp_path / 'upstream')
    git.repodir.mkdir()
    git.cmd('init', '--bare')
    yield git


@pytest.fixture
def repo_wo_remote(tmp_path):
    git = testutils.git.Git(tmp_path / 'the_repo')
    git.repodir.mkdir()
    git.cmd('init')
    config_repo(git)
    yield git


def test_repr(tmp_path):
    assert repr(testutils.git.Git(tmp_path)) == \
        f'<Git: {tmp_path}>'


def test_exists(tmp_path):
    assert testutils.git.Git(tmp_path).exists()
    assert not testutils.git.Git(tmp_path / 'foobar').exists()


def test_repodir(tmp_path):
    repo_dir = tmp_path / 'the_repo'
    git = testutils.git.Git(repo_dir)
    assert git.repodir == repo_dir


@pytest.mark.parametrize('quiet', [True, False])
def test_cmd(monkeypatch, tmp_path, quiet):
    git = testutils.git.Git(tmp_path, quiet=quiet)
    check_cmd = None
    check_stderr = None

    def mock_check_output(cmd, *args, stderr=None, **kwargs):
        # pylint: disable=unused-argument
        nonlocal check_cmd, check_stderr
        check_cmd = cmd
        check_stderr = stderr
        return b"test output\n"

    monkeypatch.setattr(subprocess, 'check_output',
                        mock_check_output)
    assert git.cmd('test', 'foobar') == "test output\n"

    assert check_cmd == ['git', '-C', tmp_path, 'test', 'foobar']
    if quiet:
        assert check_stderr == subprocess.DEVNULL
    else:
        assert check_stderr is None


def test_cmd_error(monkeypatch, tmp_path):
    git = testutils.git.Git(tmp_path)

    def mock_check_output(cmd, *args, stderr=None, **kwargs):
        # pylint: disable=unused-argument
        raise subprocess.CalledProcessError(returncode=1337, cmd=cmd)

    monkeypatch.setattr(subprocess, 'check_output',
                        mock_check_output)
    with pytest.raises(testutils.git.GitError) as exc:
        git.cmd('test', 'foobar')
        assert exc.returncode == 1337
        assert exc.cmd == ['git', '-C', tmp_path, 'test', 'foobar']


def test_clone(bare_repo, tmp_path):
    repo_dir = tmp_path / 'the_repo'
    git = testutils.git.Git.clone(bare_repo.repodir, repo_dir)
    assert (git.repodir / '.git').exists()


def test_head_sha(bare_repo):
    git = bare_repo
    # rev-parse HEAD results to HEAD when bare repo is empty
    assert git.head_sha == 'HEAD'


def test_add(repo_wo_remote):
    git = repo_wo_remote
    # list staged files
    assert not git.cmd('diff', '--name-only', '--cached')
    file = git.repodir / 'test.txt'
    file.touch()
    git.add(file)
    assert file.name in git.cmd('diff', '--name-only', '--cached')


def test_commit(repo_wo_remote):
    git = repo_wo_remote
    # git rev-parse HEAD for non-bare repo fails
    with pytest.raises(testutils.git.GitError):
        git.head_sha    # pylint: disable=pointless-statement
    git.commit('--allow-empty', '-m', 'test')
    assert re.match('[0-9a-f]{40}', git.head_sha)


def test_staging_changed(repo_wo_remote):
    git = repo_wo_remote
    # list staged files
    assert not git.staging_changed()
    file = git.repodir / 'test.txt'
    file.touch()
    git.add(file)
    assert git.staging_changed()
    git.commit('-m', 'test')
    assert not git.staging_changed()
    git.add(file)
    assert not git.staging_changed()


def test_log(repo_wo_remote):
    git = repo_wo_remote
    with pytest.raises(testutils.git.GitError):
        # no commits, so git log will fail
        git.log('--oneline').split('\n')
    test_commit(git)
    log_output = git.log('--oneline').strip().split('\n')
    assert len(log_output) == 1


def test_push(bare_repo, tmp_path):
    repo_dir = tmp_path / 'the_repo'
    git = testutils.git.Git.clone(bare_repo.repodir, repo_dir)
    config_repo(git)
    test_log(git)
    git.push()
    assert git.log() == bare_repo.log()


def test_pull(bare_repo, tmp_path):
    repo_dir2 = tmp_path / 'the_repo_new'
    git = testutils.git.Git.clone(bare_repo.repodir, repo_dir2)
    test_push(bare_repo, tmp_path)
    with pytest.raises(testutils.git.GitError):
        # no commits, so git log will fail
        git.log()
    git.pull()
    assert git.log() == bare_repo.log()
