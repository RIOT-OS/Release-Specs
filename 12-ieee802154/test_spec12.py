from time import sleep
import pytest

from riotctrl_shell.ieee802154 import IEEE802154Phy

APP = 'tests/ieee802154_hal'
PHY_MODE = 'O-QPSK'
DEFAULT_CHANNEL = 26
pytestmark = pytest.mark.rc_only()


class Shell(IEEE802154Phy):
    pass


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0', cflags="-DRIOTCTRL"),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1', cflags="-DRIOTCTRL"),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_info()[0]
    sender_addr = sender.ieee802154_print_info()[0]
    for i in range(11, 27):
        sender.ieee802154_config_phy(PHY_MODE, i, 0)
        receiver.ieee802154_config_phy(PHY_MODE, i, 0)
        sleep(2)
        sender.ieee802154_txtspam(receiver_addr, 10, 4, 100)
        sleep(2)
        receiver.ieee802154_check_last_packet(sender_addr, i)
        sleep(1)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0', cflags="-DRIOTCTRL"),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1', cflags="-DRIOTCTRL"),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_info()[0]
    res = sender.ieee802154_txtspam(receiver_addr, 10, 20, 1000)
    assert res["tx_packets"] == 20
    if res["percentage_ack"]:
        assert res["percentage_ack"] >= 90


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0', cflags="-DRIOTCTRL"),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1', cflags="-DRIOTCTRL"),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_info()[0]
    receiver.ieee802154_reply_mode_cmd("on")
    res = sender.ieee802154_txtspam(receiver_addr, 10, 10, 100)
    sleep(1)
    sender.ieee802154_check_last_packet(receiver_addr, DEFAULT_CHANNEL)
    assert res["tx_packets"] == 10
    if res["percentage_ack"]:
        assert res["percentage_ack"] >= 90
    assert res["percentage_rx"] >= 90
