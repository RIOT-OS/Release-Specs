import time
import pexpect
import pytest
from riotctrl.shell import ShellInteraction
from riotctrl_shell.netif import Ifconfig
from riotctrl_shell.gnrc import GNRCPktbufStats
from riotctrl_shell.loramac import Loramac, LoramacHelpParser
from riotctrl_shell.sys import Reboot
from testutils.shell import GNRCLoRaWANSend, ifconfig, lorawan_netif
from testutils.shell import check_pktbuf


GNRC_LORAWAN_APP = "examples/gnrc_lorawan"
LORAWAN_APP = "examples/lorawan"
SEMTECH_LORAMAC_APP = "tests/pkg/semtech-loramac"
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

# Theoretical duty cycling tx_delay for EU863-870
TEST_TX_DELAYS = {
    # see SX1276 datasheet: T_packet * 100 to ensure duty cycle of at most 1%
    # https://cdn-shop.adafruit.com/product-files/3179/sx1276_77_78_79.pdf
    # section 4.1.1.7
    # or https://loratools.nl/#/airtime (Duty Cycle or Time on air (in s) * 100)
    # based on EU868 regional parameters (v1.0.3), section 2.2.3:
    # DataRate | Configuration        | Indicative physical
    #          | (SF / BW)            | bit rate [bit/s]
    # ---------+----------------------+--------------------
    #        0 | SF12 / 125 kHz       | 250
    #        1 | SF11 / 125 kHz       | 440
    #        2 | SF10 / 125 kHz       | 980
    #        3 | SF9 / 125 kHz        | 1760
    #        4 | SF8 / 125 kHz        | 3125
    #        5 | SF7 / 125 kHz        | 5470
    #        6 | SF7 / 250 kHz        | 11000
    # payload length includes 13 bytes header + len("This is RIOT!") => 26 bytes
    0: 164.659,
    3: 20.582,
    5: 6.17,
}


class ShellGnrcLoRaWAN(Ifconfig, GNRCLoRaWANSend, GNRCPktbufStats):
    pass


class ShellLoramac(Reboot, Loramac):
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


@pytest.mark.flaky(reruns=3, reruns_delay=10)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes", [pytest.param(["b-l072z-lrwan1"])], indirect=["nodes"]
)
def test_task01(riot_ctrl, ttn_client):
    node = riot_ctrl(0, LORAWAN_APP, ShellInteraction)

    for _ in range(0, 5):
        node.riotctrl.term.expect_exact("Sending: This is RIOT!")
        time.sleep(LORAWAN_APP_PERIOD_S)
        assert ttn_client.pop_uplink_payload() == APP_PAYLOAD


@pytest.mark.flaky(reruns=3, reruns_delay=60)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes, dr",
    [
        pytest.param(["b-l072z-lrwan1"], 5),
        pytest.param(["b-l072z-lrwan1"], 3),
        pytest.param(["b-l072z-lrwan1"], 0),
    ],
    indirect=["nodes"],
)
def test_task02(riot_ctrl, ttn_client, deveui, appeui, appkey, dr):
    # pylint: disable=too-many-arguments
    node = riot_ctrl(0, SEMTECH_LORAMAC_APP, ShellLoramac)
    keys = {
        "appeui": appeui,
        "deveui": deveui,
        "appkey": appkey,
        "dr": dr,
    }

    # Set keys
    for k, v in keys.items():
        node.loramac_set(k, v)
    node.loramac_join("otaa")
    node.loramac_tx(APP_PAYLOAD, cnf=True, port=123)
    time.sleep(TEST_TX_DELAYS[dr])
    assert ttn_client.pop_uplink_payload() == APP_PAYLOAD
    node.loramac_tx(APP_PAYLOAD, cnf=False, port=42)
    time.sleep(TTN_UPLINK_DELAY)
    assert ttn_client.pop_uplink_payload() == APP_PAYLOAD


@pytest.mark.flaky(reruns=3, reruns_delay=60)
@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes, dr",
    [
        pytest.param(["b-l072z-lrwan1"], 5),
        pytest.param(["b-l072z-lrwan1"], 3),
        pytest.param(["b-l072z-lrwan1"], 0),
    ],
    indirect=["nodes"],
)
def test_task03(riot_ctrl, ttn_client, devaddr, nwkskey, appskey, dr):
    # pylint: disable=too-many-arguments
    node = riot_ctrl(0, SEMTECH_LORAMAC_APP, ShellLoramac)
    keys = {
        "appskey": appskey,
        "nwkskey": nwkskey,
        "devaddr": devaddr,
        "rx2_dr": RX2_DR,
        "dr": dr,
    }

    # Make sure the eeprom is flushed
    node.loramac_eeprom_erase()
    node.reboot()

    # Set keys
    for k, v in keys.items():
        node.loramac_set(k, v)
    node.loramac_join("abp")
    # retry sending 3 times as this is in and of it self sometimes flaky
    retries = 3
    while retries > 0:
        try:
            node.loramac_tx(APP_PAYLOAD, cnf=True, port=123, timeout=10)
            break
        except (RuntimeError, pexpect.TIMEOUT):
            retries -= 1
            time.sleep(TEST_TX_DELAYS[dr] * 2.5)
    assert retries > 0
    time.sleep(TEST_TX_DELAYS[dr])
    payload = ttn_client.pop_uplink_payload()
    assert payload == APP_PAYLOAD
    # retry sending 3 times as this is in and of it self sometimes flaky
    retries = 3
    while retries > 0:
        try:
            node.loramac_tx(APP_PAYLOAD, cnf=False, port=42, timeout=10)
            break
        except (RuntimeError, pexpect.TIMEOUT):
            retries -= 1
            time.sleep(TEST_TX_DELAYS[dr] * 2.5)
    assert retries > 0
    time.sleep(TTN_UPLINK_DELAY)
    payload = ttn_client.pop_uplink_payload()
    assert payload == APP_PAYLOAD


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes", [pytest.param(["b-l072z-lrwan1"])], indirect=["nodes"]
)
# pylint: disable=R0913
def test_task04(riot_ctrl, appeui, deveui, appkey, devaddr, nwkskey, appskey):
    node = riot_ctrl(0, SEMTECH_LORAMAC_APP, ShellLoramac)
    parser = LoramacHelpParser()

    if not parser.has_eeprom(node.loramac_help()):
        return

    # Reset values
    node.loramac_eeprom_erase()
    node.reboot()

    # Keys to test
    keys = {
        "appeui": appeui,
        "deveui": deveui,
        "appkey": appkey,
        "appskey": appskey,
        "nwkskey": nwkskey,
        "devaddr": devaddr,
    }

    # Set keys
    for k, v in keys.items():
        node.loramac_set(k, v)

    # Save and reboot
    node.loramac_eeprom_save()
    node.reboot()

    # Check saved keys
    for k, v in keys.items():
        assert v in node.loramac_get(k)


@pytest.mark.iotlab_creds
# nodes passed to riot_ctrl fixture
@pytest.mark.parametrize(
    "nodes,dev_id",
    [pytest.param(["b-l072z-lrwan1"], "otaa")],
    indirect=["nodes", "dev_id"],
)
# pylint: disable=R0913
def test_task05(riot_ctrl, ttn_client, dev_id, deveui, appeui, appkey):
    node = riot_ctrl(
        0, GNRC_LORAWAN_APP, ShellGnrcLoRaWAN, modules=["shell_cmd_gnrc_pktbuf"]
    )

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
# Missing fopts will cause it to fail on IoT-LAB(TTN, see:
# https://github.com/RIOT-OS/RIOT/issues/16962
@pytest.mark.local_only
# pylint: disable=R0913
def test_task06(riot_ctrl, ttn_client, dev_id, devaddr, nwkskey, appskey):
    node = riot_ctrl(
        0, GNRC_LORAWAN_APP, ShellGnrcLoRaWAN, modules=["shell_cmd_gnrc_pktbuf"]
    )

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
