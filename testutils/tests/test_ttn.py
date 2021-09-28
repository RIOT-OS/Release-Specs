import json
import pytest
import testutils.ttn

from testutils.ttn import SUBSCRIBE_LIST, TOPIC_ACK, TOPIC_UPLINK


BASE64_PAYLOAD = "This is RIOT!"
TEST_DEV_ID = "0102030405060708"

JSON_UPLINK = """
{
  "uplink_message": {
    "session_key_id": "AXwoG2498U/6R8SL29L1UQ==",
    "f_port": 2,
    "f_cnt": 2,
    "frm_payload": "VGhpcyBpcyBSSU9UIQ==",
    "rx_metadata": [
      {
        "gateway_ids": {
          "gateway_id": "iot-lab-saclay-gateway"
        },
        "time": "2021-09-27T16:34:49Z",
        "timestamp": 2965596547,
        "rssi": -70,
        "channel_rssi": -70,
        "snr": 10,
        "location": {
          "latitude": 48.71503122196953,
          "longitude": 2.205945253372193,
          "altitude": 157,
          "source": "SOURCE_REGISTRY"
        },
        "uplink_token": "bar"
      }
    ],
    "settings": {
      "data_rate": {
        "lora": {
          "bandwidth": 125000,
          "spreading_factor": 7
        }
      },
      "data_rate_index": 5,
      "coding_rate": "4/5",
      "frequency": "868100000",
      "timestamp": 2965596547
    },
    "received_at": "2021-09-27T16:34:49.052680760Z",
    "confirmed": true,
    "consumed_airtime": "0.061696s",
    "network_ids": {
      "net_id": "000013",
      "tenant_id": "ttn",
      "cluster_id": "ttn-eu1"
    }
  }
}
"""

JSON_UPLINK_FIRST_MSG = """
{
  "uplink_message": {
    "session_key_id": "AXwoG2498U/6R8SL29L1UQ==",
    "f_port": 2,
    "frm_payload": "VGhpcyBpcyBSSU9UIQ==",
    "rx_metadata": [
      {
        "gateway_ids": {
          "gateway_id": "iot-lab-saclay-gateway"
        },
        "time": "2021-09-27T16:34:49Z",
        "timestamp": 2965596547,
        "rssi": -70,
        "channel_rssi": -70,
        "snr": 10,
        "location": {
          "latitude": 48.71503122196953,
          "longitude": 2.205945253372193,
          "altitude": 157,
          "source": "SOURCE_REGISTRY"
        },
        "uplink_token": "foo"
      }
    ]
  }
}
"""


JSON_DOWNLINK = "{}"


class MockMQTTClient:
    def __init__(self):
        self.on_connect = None
        self.on_message = None
        self.data_set = None
        self.tls = False
        self.subscribe_list = []
        self.downlink_list = []

    @staticmethod
    def Client():
        return MockMQTTClient()

    def user_data_set(self, data_set):
        self.data_set = data_set

    def tls_set(self):
        self.tls = True

    def username_pw_set(self, user, password):
        pass

    def connect(self, url, port, ttl):
        # pylint: disable=W0613
        self.on_connect(self, self.data_set, None, None)

    def loop_start(self):
        pass

    def loop_stop(self):
        pass

    def publish(self, uri, data):
        class Downlink:
            # pylint: disable=R0903
            def __init__(self):
                self.uri = uri
                self.data = data

        self.downlink_list.append(Downlink())

    def subscribe(self, uri):
        self.subscribe_list.append(uri)

    def gen_server_push(self, topic, payload):
        class Msg:
            # pylint: disable=R0903
            def __init__(self):
                self.topic = topic
                self.payload = payload

        self.on_message(self, self.data_set, Msg())


@pytest.fixture(autouse=True)
def replace_mqtt(monkeypatch):
    monkeypatch.setenv("TTN_DL_KEY", "dl_key")
    monkeypatch.setattr(testutils.ttn, "mqtt", MockMQTTClient)


def test_on_connect(ttn_client):
    for element in ttn_client.mqtt.subscribe_list:
        assert element in SUBSCRIBE_LIST


def test_on_message_data(ttn_client):
    ttn_client.mqtt.gen_server_push(TOPIC_UPLINK, JSON_UPLINK)
    assert len(ttn_client.mqtt.data_set.msg) == 1
    assert not ttn_client.mqtt.data_set.ack


def test_on_message_ack(ttn_client):
    ttn_client.mqtt.gen_server_push(TOPIC_ACK, JSON_DOWNLINK)
    assert len(ttn_client.mqtt.data_set.msg) == 0
    assert ttn_client.mqtt.data_set.ack


def test_publish_to_dev(ttn_client):
    ttn_client.publish_to_dev(TEST_DEV_ID, foo="bar")
    downlink = ttn_client.mqtt.downlink_list.pop()
    expected_uri = f'v3/{testutils.ttn.APP_ID}@ttn/devices/{TEST_DEV_ID}/down/replace'
    assert downlink.uri == expected_uri
    assert json.loads(downlink.data)["foo"] == "bar"


def test_pop_uplink_payload(ttn_client):
    ttn_client.mqtt.gen_server_push(TOPIC_UPLINK, JSON_UPLINK)
    payload = ttn_client.pop_uplink_payload()
    assert payload == BASE64_PAYLOAD
    with pytest.raises(RuntimeError):
        ttn_client.pop_uplink_payload()


def test_downlink_ack_received(ttn_client):
    assert not ttn_client.ack

    ttn_client.ack = True
    assert ttn_client.downlink_ack_received()
