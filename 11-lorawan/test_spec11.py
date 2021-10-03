import time
import pytest
from riotctrl_shell.netif import Ifconfig
from riotctrl_shell.gnrc import GNRCPktbufStats
from testutils.shell import GNRCLoRaWANSend, ifconfig, lorawan_netif
from testutils.shell import check_pktbuf


GNRC_LORAWAN_APP = "examples/gnrc_lorawan"
pytestmark = pytest.mark.rc_only()

APP_PAYLOAD = "This is RIOT!"
DOWNLINK_PAYLOAD = "VGhpcyBpcyBSSU9U"
APP_PORT = 1
RX2_DR = 3
LORAWAN_DUTY_CYCLE_TIME = 10
LORAWAN_APP_PERIOD_S = 20
TTN_UPLINK_DELAY = 5
TTN_PORT = 1
OTAA_JOIN_DELAY = 20


class ShellGnrcLoRaWAN(Ifconfig, GNRCLoRaWANSend, GNRCPktbufStats):
    pass


def run_lw_test(node, ttn_client, iface, dev_id):
    # Disable confirmable messages
    node.ifconfig_flag(iface, "ack_req", enable=False)

    # Push a downlink message to the TTN server
    dl_data = {
        "downlinks": [
            {
                "frm_payload": DOWNLINK_PAYLOAD,
                "f_port": APP_PORT,
                "confirmed": True,
                "priority": "NORMAL",
            }
        ]
    }

    ttn_client.publish_to_dev(dev_id, **dl_data)

    # Send a message. The send function will return True if the downlink is
    # receives (as expected)
    assert node.txtsnd(iface, APP_PAYLOAD, port=TTN_PORT, timeout=10) is True
    time.sleep(LORAWAN_DUTY_CYCLE_TIME)

    assert ttn_client.pop_uplink_payload() == APP_PAYLOAD

    # Enable confirmable messages
    node.ifconfig_flag(iface, "ack_req", enable=True)

    # Send a message. In this case we shouldn't receive a downlink.
    assert node.txtsnd(iface, APP_PAYLOAD, port=TTN_PORT, timeout=10) is False

    assert ttn_client.pop_uplink_payload() == APP_PAYLOAD
    assert ttn_client.downlink_ack_received()

    check_pktbuf(node)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes,dev_id",
    [pytest.param(["b-l072z-lrwan1"], "otaa")],
    indirect=["nodes", "dev_id"],
)
# pylint: disable=R0913
def test_task05(riot_ctrl, ttn_client, dev_id, deveui, appeui, appkey):
    node = riot_ctrl(0, GNRC_LORAWAN_APP, ShellGnrcLoRaWAN, modules=["gnrc_pktbuf_cmd"])

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
    for _ in range(0, OTAA_JOIN_DELAY):
        netif = ifconfig(node, iface)
        if netif[str(iface)]["link"] == "up":
            break
        time.sleep(1)
    assert netif[str(iface)]["link"] == "up"

    run_lw_test(node, ttn_client, iface, dev_id)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes,dev_id",
    [pytest.param(["b-l072z-lrwan1"], "abp")],
    indirect=["nodes", "dev_id"],
)
# pylint: disable=R0913
def test_task06(riot_ctrl, ttn_client, dev_id, devaddr, nwkskey, appskey):
    node = riot_ctrl(0, GNRC_LORAWAN_APP, ShellGnrcLoRaWAN, modules=["gnrc_pktbuf_cmd"])

    iface = lorawan_netif(node)
    assert iface

    # Set the OTAA keys
    node.ifconfig_set(iface, "addr", devaddr)
    node.ifconfig_set(iface, "nwkskey", nwkskey)
    node.ifconfig_set(iface, "appskey", appskey)
    node.ifconfig_set(iface, "rx2_dr", RX2_DR)

    # Disable OTAA
    node.ifconfig_flag(iface, "otaa", enable=False)

    # Trigger Join Request
    node.ifconfig_up(iface)

    # Wait until the LoRaWAN network is joined
    for _ in range(0, OTAA_JOIN_DELAY):
        netif = ifconfig(node, iface)
        if netif[str(iface)]["link"] == "up":
            break
        time.sleep(1)
    assert netif[str(iface)]["link"] == "up"

    run_lw_test(node, ttn_client, iface, dev_id)
