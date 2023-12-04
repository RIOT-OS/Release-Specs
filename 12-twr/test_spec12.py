from pathlib import Path
import os
import pytest
import math
import pandas as pd
from statistics import mean
from typing import List, Tuple, Union

from riotctrl_shell.twr import TwrCmd, TwrRequestParser, TwrIfconfigParser
from riotctrl_shell.sys import Reboot
from testutils.iotlab import IoTLABExperiment


DECAWAVE_DWM_SIMPLE_LILLE_CSV = os.path.join(
    os.path.dirname(Path(__file__).resolve()), "static", "data_mean_err.csv"
)
APP = 'examples/twr_aloha'
pytestmark = pytest.mark.rc_only()

DEFAULT_TWR_ITVL = 100
DEFAULT_TWR_COUNT = 50
DEFAULT_TWR_TIMEOUT = DEFAULT_TWR_ITVL * DEFAULT_TWR_COUNT + 5 * 1000

DISTANCE_ERROR_LOS = 30


class Shell(Reboot, TwrCmd):
    """Convenience class inheriting from the Reboot and TwrCmd shell"""

    _netif = {
        "netif": None,
        "hwaddr": None,
        "hwaddr64": None,
        "panid": None,
        "channel": None,
    }

    def parse_netif(self):
        parser = TwrIfconfigParser()
        self._netif = parser.parse(self.ifconfig())

    def hwaddr(self):
        return self._netif["hwaddr"]

    def netif(self):
        return self._netif["netif"]

    def hwaddr64(self):
        return self._netif["hwaddr64"]

    def panid(self):
        return self._netif["panid"]

    def channel(self):
        return self._netif["channel"]


def _get_node_position(node: Shell) -> Union[List[float], Tuple[float, ...]]:
    """Returns the position of an IoTLAB node"""
    infos = IoTLABExperiment.get_nodes_position(node.riotctrl.env['IOTLAB_EXP_ID'])
    for info in infos:
        if info['network_address'] == node.riotctrl.env['IOTLAB_NODE']:
            return info['position']
    return (None, None, None)


def _get_nodes_distance_cm(node_0: Shell, node_1: Shell):
    """Returns euclidean distance between two IoTLAB nodes in cm"""
    node_0_pos = _get_node_position(node_0)
    node_1_pos = _get_node_position(node_1)
    # calculate euclidean distance
    d_m = math.sqrt(
        math.pow(node_0_pos[0] - node_1_pos[0], 2)
        + math.pow(node_0_pos[1] - node_1_pos[1], 2)
        + math.pow(node_0_pos[2] - node_1_pos[2], 2)
    )
    return round(d_m * 100)


@pytest.mark.iotlab_creds
@pytest.mark.flaky(reruns=3, reruns_delay=30)
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    'nodes, iotlab_site, proto',
    [
        pytest.param(['dwm1001', 'dwm1001'], "lille", "ss"),
        pytest.param(['dwm1001', 'dwm1001'], "lille", "ds"),
    ],
    indirect=['nodes', 'iotlab_site'],
)
def test_task01(riot_ctrl, proto):
    nodes = (
        riot_ctrl(0, APP, Shell),
        riot_ctrl(1, APP, Shell),
    )

    # load Decawave distance error
    df = pd.read_csv(DECAWAVE_DWM_SIMPLE_LILLE_CSV, index_col=0)

    for node in nodes:
        node.parse_netif()

    for initiator, responder in zip(nodes, nodes[::-1]):
        responder.twr_listen(on=True)
        out = initiator.twr_request(
            addr=responder.hwaddr(),
            count=DEFAULT_TWR_COUNT,
            itvl=DEFAULT_TWR_ITVL,
            proto=proto,
            timeout=DEFAULT_TWR_TIMEOUT,
        )
        req_parser = TwrRequestParser()
        d_cm = req_parser.parse(out)

        assert mean(d_cm) > 0
        # If ran on IoTLAB also check that error is within margin
        if 'IOTLAB_NODE' in responder.riotctrl.env:
            d_error_cm = abs(mean(d_cm) - _get_nodes_distance_cm(responder, initiator))
            # sanity check distance error should not be above 1m
            assert d_error_cm < 100
            deca_d_error_cm = df[initiator.hwaddr()][responder.hwaddr()]
            # if Decawave PANS R2 error is under 30cm consider it ~LOS conditions,
            # and therefore RIOT should show a similar error
            if deca_d_error_cm < DISTANCE_ERROR_LOS:
                assert d_error_cm < DISTANCE_ERROR_LOS
        responder.twr_listen(on=False)
