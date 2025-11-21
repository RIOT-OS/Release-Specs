import pytest

import testutils.iotlab


# pylint: disable=R0903
class MockRIOTCtrl:
    def __init__(self, env):
        self.env = env

    def board(self):
        return self.env.get("BOARD")


@pytest.mark.parametrize(
    "iotlab_node,expected",
    [
        ("arduino-zero-1.saclay.iot-lab.info", "arduino-zero"),
        ("st-lrwan1-2.saclay.iot-lab.info", "b-l072z-lrwan1"),
        ("st-iotnode-3.saclay.iot-lab.info", "b-l475e-iot01a"),
        ("firefly-10.lille.iot-lab.info", "firefly"),
        ("frdm-kw41z-4.saclay.iot-lab.info", "frdm-kw41z"),
        ("a8-125.grenoble.iot-lab.info", "iotlab-a8-m3"),
        ("m3-23.lyon.iot-lab.info", "iotlab-m3"),
        ("microbit-5.saclay.iot-lab.info", "microbit"),
        ("nrf51dk-2.saclay.iot-lab.info", "nrf51dk"),
        ("nrf52dk-6.saclay.iot-lab.info", "nrf52dk"),
        ("nrf52832mdk-1.saclay.iot-lab.info", "nrf52832-mdk"),
        ("nrf52840dk-7.saclay.iot-lab.info", "nrf52840dk"),
        ("nrf52840mdk-1.saclay.iot-lab.info", "nrf52840-mdk"),
        ("phynode-1.saclay.iot-lab.info", "pba-d-01-kw2x"),
        ("samr21-19.saclay.iot-lab.info", "samr21-xpro"),
        ("samr30-3.saclay.iot-lab.info", "samr30-xpro"),
    ],
)
def test_board_from_iotlab_node(iotlab_node, expected):
    assert (
        testutils.iotlab.IoTLABExperiment.board_from_iotlab_node(iotlab_node)
        == expected
    )


def test_board_from_iotlab_node_invalid():
    with pytest.raises(ValueError):
        testutils.iotlab.IoTLABExperiment.board_from_iotlab_node("foobar")


def test_valid_board():
    assert testutils.iotlab.IoTLABExperiment.valid_board(
        next(iter(testutils.iotlab.IoTLABExperiment.BOARD_ARCHI_MAP))
    )


def test_invalid_board():
    assert not testutils.iotlab.IoTLABExperiment.valid_board("ghgsoqwczoe")


@pytest.mark.parametrize(
    "iotlab_node,site,board",
    [
        ("m3-84.grenoble.iot-lab.info", "grenoble", None),
        ("a8-11.lyon.iot-lab.info", "lyon", None),
        ("m3-84.lille.iot-lab.info", "lille", "iotlab-m3"),
        ("a8-84.saclay.iot-lab.info", "saclay", "iotlab-a8-m3"),
    ],
)
def test_valid_iotlab_node(iotlab_node, site, board):
    testutils.iotlab.IoTLABExperiment.valid_iotlab_node(iotlab_node, site, board)


@pytest.mark.parametrize(
    "iotlab_node,site,board",
    [
        ("m3-84.grenoble.iot-lab.info", "lyon", None),
        ("wuadngum", "gvcedudng", None),
        ("m3-84.lille.iot-lab.info", "lille", "samr21-xpro"),
        ("a8-84.saclay.iot-lab.info", "saclay", "eauneguä"),
    ],
)
def test_invalid_iotlab_node(iotlab_node, site, board):
    with pytest.raises(ValueError):
        testutils.iotlab.IoTLABExperiment.valid_iotlab_node(iotlab_node, site, board)


def test_user_credentials(monkeypatch):
    creds = ("user", "password")
    monkeypatch.setattr(testutils.iotlab, "get_user_credentials", lambda: creds)
    assert testutils.iotlab.IoTLABExperiment.user_credentials() == creds


def test_check_user_credentials(monkeypatch):
    monkeypatch.setattr(
        testutils.iotlab, "get_user_credentials", lambda: ("user", "password")
    )
    assert testutils.iotlab.IoTLABExperiment.check_user_credentials()


def test_check_user_credentials_unset(monkeypatch):
    monkeypatch.setattr(testutils.iotlab, "get_user_credentials", lambda: (None, None))
    assert not testutils.iotlab.IoTLABExperiment.check_user_credentials()


@pytest.mark.parametrize(
    "ctrl_envs,args,exp_boards",
    [
        (
            [{"IOTLAB_NODE": "m3-23.saclay.iot-lab.info", "BOARD": "iotlab-m3"}],
            (),
            ["iotlab-m3"],
        ),
        ([{"IOTLAB_NODE": "m3-23.saclay.iot-lab.info"}], (), ["iotlab-m3"]),
        ([{"BOARD": "iotlab-m3"}], (), ["iotlab-m3"]),
        (
            [{"IOTLAB_NODE": "m3-23.saclay.iot-lab.info", "BOARD": "iotlab-m3"}],
            ("saclay",),
            ["iotlab-m3"],
        ),
        (
            [{"IOTLAB_NODE": "m3-23.grenoble.iot-lab.info"}],
            ("grenoble",),
            ["iotlab-m3"],
        ),
        ([{"BOARD": "iotlab-m3"}], ("lille",), ["iotlab-m3"]),
    ],
)
def test_init(ctrl_envs, args, exp_boards):
    assert testutils.iotlab.DEFAULT_SITE == "saclay"
    ctrls = [MockRIOTCtrl(env) for env in ctrl_envs]
    exp = testutils.iotlab.IoTLABExperiment("test", ctrls, *args)
    if args:
        assert exp.site == args[0]
    else:
        assert exp.site == "saclay"
    assert exp.ctrls == ctrls
    for ctrl, exp_board in zip(exp.ctrls, exp_boards):
        assert ctrl.board() == exp_board
    assert exp.name == "test"
    assert exp.exp_id is None


@pytest.mark.parametrize(
    "ctrl_envs,args",
    [
        (
            [{"IOTLAB_NODE": "m3-23.saclay.iot-lab.info", "BOARD": "iotlab-m3"}],
            ("khseaip",),
        ),
        ([{"BOARD": "uaek-eaqfgnic"}], ()),
        ([{"IOTLAB_NODE": "go5wxbp-124.saclay.iot-lab.info"}], ()),
        ([{}], ()),
    ],
)
def test_init_value_error(ctrl_envs, args):
    ctrls = [MockRIOTCtrl(env) for env in ctrl_envs]
    with pytest.raises(ValueError):
        testutils.iotlab.IoTLABExperiment("test", ctrls, *args)


@pytest.mark.parametrize("exp_id,expected", [(None, None), (1234, "This is a test")])
def test_stop(monkeypatch, exp_id, expected):
    monkeypatch.setattr(
        testutils.iotlab.IoTLABExperiment,
        "user_credentials",
        lambda cls: ("user", "password"),
    )
    monkeypatch.setattr(testutils.iotlab, "Api", lambda user, password: None)
    monkeypatch.setattr(
        testutils.iotlab, "stop_experiment", lambda api, exp_id: expected
    )
    ctrls = [MockRIOTCtrl({"BOARD": "iotlab-m3"})]
    exp = testutils.iotlab.IoTLABExperiment("test", ctrls)
    exp.exp_id = exp_id
    assert exp.stop() == expected


@pytest.mark.parametrize(
    "ctrl_envs, exp_nodes",
    [
        ([{"BOARD": "nrf52dk"}], ["nrf52dk-5.saclay.iot-lab.info"]),
        ([{"BOARD": "iotlab-m3"}], ["m3-3.saclay.iot-lab.info"]),
        (
            [{"IOTLAB_NODE": "samr21-21.saclay.iot-lab.info"}],
            ["samr21-21.saclay.iot-lab.info"],
        ),
    ],
)
def test_start(monkeypatch, ctrl_envs, exp_nodes):
    monkeypatch.setattr(
        testutils.iotlab.IoTLABExperiment,
        "user_credentials",
        lambda cls: ("user", "password"),
    )
    monkeypatch.setattr(testutils.iotlab, "Api", lambda user, password: None)
    monkeypatch.setattr(testutils.iotlab, "exp_resources", lambda arg: arg)
    monkeypatch.setattr(
        testutils.iotlab,
        "submit_experiment",
        lambda api, name, duration, resources: {"id": 12345},
    )
    monkeypatch.setattr(
        testutils.iotlab, "get_experiment", lambda api, exp_id: {"nodes": exp_nodes}
    )
    monkeypatch.setattr(
        testutils.iotlab,
        "info_experiment",
        lambda api, site: {
            "items": [
                {
                    "state": "Alive",
                    "network_address": exp_nodes[0],
                },
            ],
        },
    )
    monkeypatch.setattr(testutils.iotlab, "wait_experiment", lambda api, exp_id: {})
    ctrls = [MockRIOTCtrl(env) for env in ctrl_envs]
    exp = testutils.iotlab.IoTLABExperiment("test", ctrls)
    exp.start()
    assert exp.exp_id == 12345


def test_start_error(monkeypatch):
    monkeypatch.setattr(
        testutils.iotlab.IoTLABExperiment,
        "user_credentials",
        lambda cls: ("user", "password"),
    )
    monkeypatch.setattr(testutils.iotlab, "Api", lambda user, password: None)
    ctrls = [MockRIOTCtrl({'BOARD': 'iotlab-m3'})]
    exp = testutils.iotlab.IoTLABExperiment("test", ctrls)
    ctrls[0].env.pop("BOARD")
    with pytest.raises(ValueError):
        exp.start()
