from time import sleep
import pytest
import riotctrl


from riotctrl_shell.ieee802154 import Config_phy, Print_addr, Txtsnd

APP = 'tests/ieee802154_hal'
pytestmark = pytest.mark.rc_only()


class Shell(Config_phy, Print_addr, Txtsnd):
    pass


@pytest.mark.parametrize('nodes',
                         [pytest.param(['remote-revb', 'remote-revb'])],
                         indirect=['nodes'])
def test_task01(riot_ctrl):
    print(riotctrl)
    sender, receiver = (
        riot_ctrl(0, APP, Shell, port='/dev/ttyUSB0'),
        riot_ctrl(1, APP, Shell, port='/dev/ttyUSB1'),
    )
    print("--------------------------------------------------------------------------")
    sender.tx_mode("direct")
    receiver.tx_mode("direct")
    receiver_addr = receiver.print_addr()
    sender_addr = sender.print_addr()
    for i in range(11, 27):
        sender.config_phy(i, 0)
        receiver.config_phy(i, 0)
        sleep(0.2)
        sender.txtsnd(receiver_addr)
        sleep(0.2)
        receiver.check_last_packet(sender_addr, i)
        sleep(0.2)
