import os
import json
import logging
import subprocess
import re

from testutils import Board

class IoTLABNode(object):
    BOARD_ARCHI_MAP = {
            "iotlab-m3": {"archi": "m3", "radio": "at86rf231"},
            "samr21-xpro": {"archi": "samr21", "radio": "at86rf233"},
            "arduino-zero": {"archi": "arduino-zero", "radio": "xbee"},
        }
    SITES = ["grenoble", "saclay"]

    def __init__(self, board="iotlab-m3", site="grenoble",
                 extra_modules=[]):
        assert(board in IoTLABNode.BOARD_ARCHI_MAP)
        assert(site in IoTLABNode.SITES)
        self.board = board
        self.site = site
        self.extra_modules = extra_modules
        self.exp = None
        self.addr = None

    def __repr__(self):
        return "IoTLABNode(board={}, site={}, " \
               "extra_modules={}, addr={})".format(
                self.board, self.site, self.extra_modules, self.addr)

    def addr_points_to_node(self, addr):
        if self.addr is None:
            if addr.startswith(
                    IoTLABNode.BOARD_ARCHI_MAP[self.board]["archi"] + "-"):
                self.addr = addr
                return True
            return False
        else:
            return addr == self.addr

    def flash(self, addr):
        assert(self.exp is not None)
        env = os.environ
        env["BOARD"] = self.board
        env["USEMODULE"] = " ".join(self.extra_modules)
        env["IOTLAB_NODE"] = addr
        env["IOTLAB_EXP_ID"] = self.exp.exp_id
        logging.info("Flashing test binary to {}".format(addr))
        subprocess.run(["make", "flash"], env=env)

    @property
    def exp_param(self):
        board = IoTLABNode.BOARD_ARCHI_MAP[self.board]
        return "-l1,archi={}:{}+site={}".format(
                board["archi"], board["radio"], self.site
            )


# Thrown when there is an error with the *interaction* with the IoTLAB
# experiment (e.g. if the iotlab-experiment command fails for any reason)
class IoTLABExperimentError(Exception):
    pass


class IoTLABExperiment(object):
    def __init__(self, name, nodes):
        self.nodes = nodes
        self.name = name
        self.exp_id = None
        try:
            self.exp_id = subprocess.check_output(
                    ["iotlab-experiment", "--jmespath", "@.id",
                        "--format", "int", "submit", "-n", name, "-d", "30"] +
                    [node.exp_param for node in nodes],
                    stderr=subprocess.PIPE
                ).strip().decode("utf-8")
            logging.info("Waiting for experiment", self.exp_id,
                         "to go to state \"Running\"")
            subprocess.run(["iotlab-experiment", "wait", "-i", self.exp_id],
                           stderr=subprocess.PIPE, check=True)
            addrs = self._get_nodes_addresses()
            for node in nodes:
                addr = next(a for a in addrs if node.addr_points_to_node(a))
                node.exp = self
                node.flash(addr)
                addrs.remove(addr)
        except subprocess.CalledProcessError as e:
            self.stop()
            raise IoTLABExperimentError(e.stderr.decode("utf-8"))
        self.exp_id = int(self.exp_id)

    def __repr__(self):
        return "IoTLABExperiment(name={}, exp_id={})".format(self.name,
                                                             self.exp_id)

    def stop(self):
        if self.exp_id is not None:
            subprocess.check_call(['iotlab-experiment', 'stop',
                                   '-i', str(self.exp_id)])

    @property
    def nodes_addresses(self):
        return [node.addr for node in self.nodes]

    def _get_nodes_addresses(self):
        output = subprocess.check_output(
                ['iotlab-experiment', 'get', '-i', str(self.exp_id), '-r'],
            ).decode("utf-8")
        res = json.loads(output)
        l = []
        for i in res["items"]:
            l.append(i["network_address"])

        return l
