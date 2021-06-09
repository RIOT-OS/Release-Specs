from time import sleep
import pytest

from riotctrl_shell.ieee802154 import IEEE802154Phy

APP = 'tests/ieee802154_hal'
PHY_MODE = 'O-QPSK'
DEFAULT_CHANNEL = 26
pytestmark = pytest.mark.rc_only()


class Shell(IEEE802154Phy):
    pass


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_addr()
    sender_addr = sender.ieee802154_print_addr()
    for i in range(11, 27):
        sender.ieee802154_config_phy(PHY_MODE, i, 0)
        receiver.ieee802154_config_phy(PHY_MODE, i, 0)
        sleep(1)
        sender.ieee802154_txtspam(receiver_addr, 1, 0)
        sleep(1)
        receiver.ieee802154_check_last_packet(sender_addr, i)
        sleep(0.5)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_addr()
    sender.ieee802154_txtspam(receiver_addr, 5, 1000)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.ieee802154_tx_mode("direct")
    receiver.ieee802154_tx_mode("direct")
    receiver_addr = receiver.ieee802154_print_addr()
    receiver.ieee802154_reply()
    sender.ieee802154_txtsnd(receiver_addr, 1)
    sleep(1)
    sender.ieee802154_check_last_packet(receiver_addr, DEFAULT_CHANNEL)
