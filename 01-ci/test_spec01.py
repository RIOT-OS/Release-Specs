import os
import subprocess

import pytest

APP = 'tests/unittests'
TESTS_SUITES = sorted(
    d.name
    for d in os.scandir(os.path.join(os.environ['RIOTBASE'], APP))
    if d.is_dir() and d.name.startswith('tests-')
)
pytestmark = pytest.mark.rc_only()


def run_unittests(target, nodes, log_nodes, app_dir):
    node = nodes[0]
    # need to access private member here isn't possible otherwise sadly :(
    # pylint: disable=W0212
    node._application_directory = app_dir
    node.make_run(
        [target, 'flash-only', 'test'],
        check=True,
        stdout=None if log_nodes else subprocess.DEVNULL,
        stderr=None if log_nodes else subprocess.DEVNULL,
    )


# nodes passed to nodes fixture
@pytest.mark.parametrize('nodes', [pytest.param(['native'])], indirect=['nodes'])
def test_task02(nodes, log_nodes, riotbase):
    run_unittests('all', nodes, log_nodes, os.path.join(riotbase, APP))


# nodes passed to nodes fixture
@pytest.mark.parametrize(
    'nodes, test_suite',
    [pytest.param(['native'], t) for t in TESTS_SUITES],
    indirect=['nodes'],
)
def test_task03(nodes, log_nodes, riotbase, test_suite):
    run_unittests(test_suite, nodes, log_nodes, os.path.join(riotbase, APP))


@pytest.mark.iotlab_creds
# nodes passed to nodes fixture
@pytest.mark.parametrize('nodes', [pytest.param(['iotlab-m3'])], indirect=['nodes'])
def test_task04(nodes, log_nodes, riotbase):
    run_unittests('all', nodes, log_nodes, os.path.join(riotbase, APP))

# nodes passed to nodes fixture
@pytest.mark.parametrize('nodes', [pytest.param(['native64'])], indirect=['nodes'])
def test_task05(nodes, log_nodes, riotbase):
    run_unittests('all', nodes, log_nodes, os.path.join(riotbase, APP))
