import logging
import random
import re

from iotlabcli.auth import get_user_credentials
from iotlabcli.rest import Api
from iotlabcli.experiment import (
    submit_experiment,
    wait_experiment,
    stop_experiment,
    get_experiment,
    exp_resources,
    info_experiment,
    AliasNodes,
)


DEFAULT_SITE = 'saclay'
IOTLAB_DOMAIN = 'iot-lab.info'


class IoTLABExperiment:
    """Utility for running iotlab-experiments based on a list of RIOTCtrls
    expects BOARD or IOTLAB_NODE variable to be set for received nodes"""

    BOARD_ARCHI_MAP = {
        'arduino-zero': {'name': 'arduino-zero', 'radio': 'xbee'},
        'b-l072z-lrwan1': {'name': 'st-lrwan1', 'radio': 'sx1276'},
        'b-l475e-iot01a': {'name': 'st-iotnode', 'radio': 'multi'},
        'firefly': {'name': 'firefly', 'radio': 'multi'},
        'frdm-kw41z': {'name': 'frdm-kw41z', 'radio': 'multi'},
        'iotlab-a8-m3': {'name': 'a8', 'radio': 'at86rf231'},
        'iotlab-m3': {'name': 'm3', 'radio': 'at86rf231'},
        'microbit': {'name': 'microbit', 'radio': 'ble'},
        'nrf51dk': {'name': 'nrf51dk', 'radio': 'ble'},
        'nrf52dk': {'name': 'nrf52dk', 'radio': 'ble'},
        'nrf52832-mdk': {'name': 'nrf52832mdk', 'radio': 'ble'},
        'nrf52840dk': {'name': 'nrf52840dk', 'radio': 'multi'},
        'nrf52840-mdk': {'name': 'nrf52840mdk', 'radio': 'multi'},
        'openmote-b': {'name': 'openmoteb'},
        'pba-d-01-kw2x': {'name': 'phynode', 'radio': 'kw2xrf'},
        'samr21-xpro': {'name': 'samr21', 'radio': 'at86rf233'},
        'samr30-xpro': {'name': 'samr30', 'radio': 'at86rf212b'},
    }

    SITES = ['grenoble', 'lille', 'saclay', 'strasbourg']

    def __init__(self, name, ctrls, site=DEFAULT_SITE):
        IoTLABExperiment._check_site(site)
        self.site = site
        IoTLABExperiment._check_ctrls(site, ctrls)
        self.ctrls = ctrls
        self.name = name
        self.exp_id = None

    @staticmethod
    def board_from_iotlab_node(iotlab_node):
        """Return BOARD matching iotlab_node"""
        reg = r'([0-9a-zA-Z\-]+)-\d+\.[a-z]+\.iot-lab\.info'
        match = re.search(reg, iotlab_node)
        if match is None:
            raise ValueError(
                f"Unable to parse {iotlab_node} as IoT-LAB node "
                "name of format "
                "<node-name>.<site-name>.iot-lab.info"
            )
        iotlab_node_name = match.group(1)
        dict_values = IoTLABExperiment.BOARD_ARCHI_MAP.values()
        dict_names = [value['name'] for value in dict_values]
        dict_keys = list(IoTLABExperiment.BOARD_ARCHI_MAP.keys())
        return dict_keys[dict_names.index(iotlab_node_name)]

    @staticmethod
    def valid_board(board):
        return board in IoTLABExperiment.BOARD_ARCHI_MAP

    @staticmethod
    def valid_iotlab_node(iotlab_node, site, board=None):
        if site not in iotlab_node:
            raise ValueError("All nodes must be on the same site")
        if board is not None:
            if IoTLABExperiment.board_from_iotlab_node(iotlab_node) != board:
                raise ValueError("IOTLAB_NODE doesn't match BOARD")

    @classmethod
    def check_user_credentials(cls):
        res = cls.user_credentials()
        return res != (None, None)

    @staticmethod
    def user_credentials():
        return get_user_credentials()

    @staticmethod
    def _archi_from_board(board):
        """Return iotlab 'archi' format for BOARD"""
        name = IoTLABExperiment.BOARD_ARCHI_MAP[board]['name']
        if 'radio' not in IoTLABExperiment.BOARD_ARCHI_MAP[board]:
            return f'{name}'
        radio = IoTLABExperiment.BOARD_ARCHI_MAP[board]['radio']
        return f'{name}:{radio}'

    @staticmethod
    def _check_site(site):
        if site not in IoTLABExperiment.SITES:
            raise ValueError("iotlab site must be one of " f"{IoTLABExperiment.SITES}")

    @staticmethod
    def _valid_addr(ctrl, addr):
        """Check id addr matches a specific RIOTCtrl BOARD"""
        return addr.startswith(IoTLABExperiment.BOARD_ARCHI_MAP[ctrl.board()]['name'])

    @staticmethod
    def _check_ctrls(site, ctrls):
        """Takes a list of RIOTCtrls and validates BOARD or IOTLAB_NODE"""
        for ctrl in ctrls:
            # If BOARD is set it must be supported in iotlab
            if ctrl.board() is not None:
                if not IoTLABExperiment.valid_board(ctrl.board()):
                    raise ValueError(f"{ctrl} BOARD unsupported in iotlab")
                if ctrl.env.get('IOTLAB_NODE') is not None:
                    IoTLABExperiment.valid_iotlab_node(
                        ctrl.env['IOTLAB_NODE'], site, ctrl.board()
                    )
            elif ctrl.env.get('IOTLAB_NODE') is not None:
                IoTLABExperiment.valid_iotlab_node(ctrl.env['IOTLAB_NODE'], site)
                board = IoTLABExperiment.board_from_iotlab_node(ctrl.env["IOTLAB_NODE"])
                ctrl.env['BOARD'] = board
            else:
                raise ValueError("BOARD or IOTLAB_NODE must be set")

    def stop(self):
        """If running stop the experiment"""
        ret = None
        if self.exp_id is not None:
            ret = stop_experiment(Api(*self.user_credentials()), self.exp_id)
            self.exp_id = None
        return ret

    def start(self, duration=60):
        """Submit an experiment, wait for it to be ready and map assigned
        nodes"""
        logging.info("Submitting experiment")
        self.exp_id = self._submit(site=self.site, duration=duration)
        logging.info(
            f"Waiting for experiment {self.exp_id} to go to state " "\"Running\""
        )
        self._wait()
        self._map_iotlab_nodes_to_riot_ctrl(self._get_nodes())

    def _wait(self):
        """Wait for the experiment to finish launching"""
        ret = wait_experiment(Api(*self.user_credentials()), self.exp_id)
        return ret

    def _select_random_node(self, site, board):
        api = Api(*self.user_credentials())
        info = info_experiment(api, site=site)
        choices = []
        for iot_lab_nodes in info.values():
            if not isinstance(iot_lab_nodes, list):
                continue
            for iot_lab_node in iot_lab_nodes:
                if iot_lab_node.get("state", "") != "Alive":
                    continue
                net_addr = iot_lab_node.get("network_address", "")
                if board not in net_addr:
                    continue
                choices.append(net_addr)
        if not choices:
            raise RuntimeError(f"No {board} found at {site}")
        ret = random.choice(choices)
        return ret

    def _submit(self, site, duration):
        """Submit an experiment with required nodes"""
        api = Api(*self.user_credentials())
        resources = []
        for ctrl in self.ctrls:
            if ctrl.env.get('IOTLAB_NODE') is not None:
                resources.append(exp_resources([ctrl.env.get('IOTLAB_NODE')]))
            elif ctrl.board() is not None:
                # Since we cannot combine alias and phyical nodes in the same
                # experiment and but we would prefer to use iotlab-m3 alias
                # nodes because the m3 nodes can report that they are broken.
                # Let's take the easiest solution and only use alias nodes
                # if they are all iotlab-m3 nodes.
                if all(ctrl.board() == 'iotlab-m3' for ctrl in self.ctrls):
                    board = IoTLABExperiment._archi_from_board(ctrl.board())
                    alias = AliasNodes(1, site, board)
                    resources.append(exp_resources(alias))
                else:
                    board = IoTLABExperiment.BOARD_ARCHI_MAP[ctrl.board()]['name']
                    net_addr = self._select_random_node(site, board)
                    resources.append(exp_resources([net_addr]))
            else:
                raise ValueError("neither BOARD or IOTLAB_NODE are set")
        return submit_experiment(api, self.name, duration, resources)['id']

    def _map_iotlab_nodes_to_riot_ctrl(self, iotlab_nodes):
        """Fetch reserved nodes and map each one to an RIOTCtrl"""
        for ctrl in self.ctrls:
            if ctrl.env.get('IOTLAB_NODE') in iotlab_nodes:
                iotlab_nodes.remove(ctrl.env['IOTLAB_NODE'])
            else:
                for iotlab_node in iotlab_nodes:
                    if IoTLABExperiment._valid_addr(ctrl, iotlab_node):
                        iotlab_nodes.remove(iotlab_node)
                        ctrl.env['IOTLAB_NODE'] = str(iotlab_node)
                        break
            ctrl.env['IOTLAB_EXP_ID'] = str(self.exp_id)

    def _get_nodes(self):
        """Return all nodes reserved by the experiment"""
        ret = get_experiment(Api(*self.user_credentials()), self.exp_id)
        return ret['nodes']
