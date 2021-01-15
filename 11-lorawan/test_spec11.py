import time
import pytest
from testutils.shell import GNRCLoRaWANSend, ifconfig, lorawan_netif
from riotctrl_shell.netif import Ifconfig
import base64
import json

APP = 'examples/gnrc_lorawan'
pytestmark = pytest.mark.rc_only()

APP_PAYLOAD = "This is RIOT!"
DOWNLINK_PAYLOAD = "VGhpcyBpcyBSSU9U"
APP_PORT = 2
RX2_DR = 3


class Shell(Ifconfig, GNRCLoRaWANSend):
    pass


def run_lw_test(node, client, userdata, iface, app_id, dev_id):
    # Disable confirmable messages
    node.ifconfig_flag(iface, "ack_req", enable=False)

    # Push a downlink message to the TTN server
    dl_data = {"payload_raw": DOWNLINK_PAYLOAD, "port": APP_PORT,
               "confirmed": True}

    client.publish("{}/devices/{}/down".format(app_id, dev_id),
                   json.dumps(dl_data))

    # Send a message. The send function will return True if the downlink is
    # receives (as expected)
    assert node.send(iface, APP_PAYLOAD) is True
    time.sleep(3)

    message = base64.b64decode(userdata["msg"]["payload_raw"])
    assert message.decode('ascii') == APP_PAYLOAD

    # Enable confirmable messages
    node.ifconfig_flag(iface, "ack_req", enable=True)

    # Send a message. In this case we shouldn't receive a downlink.
    assert node.send(iface, APP_PAYLOAD) is False

    message = base64.b64decode(userdata["msg"]["payload_raw"])
    assert message.decode('ascii') == APP_PAYLOAD


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes,dev_id',
                         [pytest.param(['b-l072z-lrwan1'], "otaa")],
                         indirect=['nodes', 'dev_id'])
def test_task05(riot_ctrl, mqtt_client, app_id, dev_id, deveui,
                appeui, appkey):
    node = riot_ctrl(0, APP, Shell)

    client = mqtt_client.client
    userdata = mqtt_client.userdata

    iface = lorawan_netif(node)
    assert iface

    # Set the OTAA keys
    node.ifconfig_set(iface, "deveui", deveui)
    node.ifconfig_set(iface, "appeui", appeui)
    node.ifconfig_set(iface, "appkey", appkey)

    # Enable OTAA
    node.ifconfig_flag(iface, "otaa", enable=True)

    # Trigger Join Request
    node.ifconfig_up(iface)

    # Wait until the LoRaWAN network is joined
    time.sleep(10)

    netif = ifconfig(node, iface)
    assert netif[str(iface)]["link"] == "up"

    run_lw_test(node, client, userdata, iface, app_id, dev_id)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize('nodes,dev_id',
                         [pytest.param(['b-l072z-lrwan1'], "abp")],
                         indirect=['nodes', 'dev_id'])
def test_task06(riot_ctrl, mqtt_client, app_id, dev_id,
                devaddr, nwkskey, appskey):
    node = riot_ctrl(0, APP, Shell)

    client = mqtt_client.client
    userdata = mqtt_client.userdata

    iface = lorawan_netif(node)
    assert iface

    # Set the OTAA keys
    node.ifconfig_set(iface, "addr", devaddr)
    node.ifconfig_set(iface, "nwkskey", nwkskey)
    node.ifconfig_set(iface, "appskey", appskey)
    node.ifconfig_set(iface, "rx2_dr", RX2_DR)

    # Enable OTAA
    node.ifconfig_flag(iface, "otaa", enable=False)

    # Trigger Join Request
    node.ifconfig_up(iface)

    # Wait until the LoRaWAN network is joined
    time.sleep(10)

    netif = ifconfig(node, iface)
    assert netif[str(iface)]["link"] == "up"

    run_lw_test(node, client, userdata, iface, app_id, dev_id)
