import json
import pytest
import testutils.ttn

TOPIC_UPLINK = '+/devices/+/up'
TOPIC_ACK = '+/devices/+/events/down/acks'
TOPIC_ACTIVATION = '+/devices/+/events/activations'
SUBSCRIBE_LIST = [TOPIC_UPLINK, TOPIC_ACTIVATION, TOPIC_ACK]

BASE64_PAYLOAD = '\x01\x02\x03\x04'
TEST_DEV_ID = "0102030405060708"

JSON_UPLINK = """{
  "app_id": "my-app-id",
  "dev_id": "my-dev-id",
  "hardware_serial": "0102030405060708",
  "port": 1,
  "counter": 2,
  "is_retry": false,
  "confirmed": false,
  "payload_raw": "AQIDBA==",
  "payload_fields": {},
  "metadata": {
    "airtime": 46336000,
    "time": "1970-01-01T00:00:00Z",
    "frequency": 868.1,
    "modulation": "LORA",
    "data_rate": "SF7BW125",
    "bit_rate": 50000,
    "coding_rate": "4/5",
    "gateways": [
      {
        "gtw_id": "ttn-herengracht-ams",
        "timestamp": 12345,
        "time": "1970-01-01T00:00:00Z",
        "channel": 0,
        "rssi": -25,
        "snr": 5,
        "rf_chain": 0,
        "latitude": 52.1234,
        "longitude": 6.1234,
        "altitude": 6
      }
    ],
    "latitude": 52.2345,
    "longitude": 6.2345,
    "altitude": 2
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
    monkeypatch.setenv("LORAWAN_DL_KEY", "dl_key")
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
    expected_uri = '{}/devices/{}/down'.format(testutils.ttn.APP_ID,
                                               TEST_DEV_ID)
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
