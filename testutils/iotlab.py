import pexpect
import json
import subprocess
import re

IOTLAB_SITE = "grenoble"


def create_experiment(nodes):
    output = pexpect.run(
            'make BOARD=iotlab-m3 IOTLAB_NODES={} IOTLAB_SITE={} iotlab-exp'
            .format(nodes, IOTLAB_SITE), timeout=600, encoding="utf-8")

    m = re.search(
            'Waiting that experiment ([0-9]+) gets in state Running', output)

    if m and m.group(1):
        expId = m.group(1)
    else:
        print("Experiment id could not be parsed")
        return None
    return expId


def stop_experiment(exp_id):
    subprocess.check_call(['iotlab-experiment', 'stop', '-i', str(exp_id)])


def get_nodes_addresses(exp_id):
    output = subprocess.check_output(
            ['iotlab-experiment', 'get', '-i', str(exp_id), '-r'],
            encoding="utf-8")

    res = json.loads(output)
    addresses = []
    for i in res["items"]:
        addresses.append(i["network_address"])

    return addresses
