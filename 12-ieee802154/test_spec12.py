from time import sleep
import pytest

from riotctrl_shell.ieee802154 import Config_phy, Print_addr, Txtsnd

APP = 'tests/ieee802154_hal'
PHY_MODE = 'O-QPSK'
DEFAULT_CHANNEL = 26
pytestmark = pytest.mark.rc_only()


class Shell(Config_phy, Print_addr, Txtsnd):
    pass


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.tx_mode("direct")
    receiver.tx_mode("direct")
    receiver_addr = receiver.print_addr()
    sender_addr = sender.print_addr()
    for i in range(11, 27):
        sender.config_phy(PHY_MODE, i, 0)
        receiver.config_phy(PHY_MODE, i, 0)
        sleep(0.5)
        sender.txtsnd(receiver_addr, 1, 0)
        sleep(0.5)
        receiver.check_last_packet(sender_addr, i)
        sleep(0.5)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task02(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.tx_mode("direct")
    receiver.tx_mode("direct")
    receiver_addr = receiver.print_addr()
    sender.txtsnd(receiver_addr, 5, 1000)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task03(riot_ctrl):
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    sender.tx_mode("direct")
    receiver.tx_mode("direct")
    receiver_addr = receiver.print_addr()
    receiver.reply()
    sender.txtsnd(receiver_addr, 1, 0)
    sleep(1)
    sender.check_last_packet(receiver_addr, DEFAULT_CHANNEL)
