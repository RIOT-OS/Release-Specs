import os
import re
import json
import base64

import paho.mqtt.client as mqtt
from testutils.pytest import get_required_envvar

APP_ID = os.environ.get("TTN_APP_ID", "riot-test")
DEVICE_ID = os.environ.get("TTN_DEV_ID", "riot-examples-lorawan-otaa")
DEVICE_ID_ABP = os.environ.get("TTN_DEV_ID_ABP", "riot_lorawan_1_abp")
TTN_MQTT_SERVER = os.environ.get("TTN_MQTT_SERVER", "eu1.cloud.thethings.network")

TOPIC_UPLINK = 'v3/+/devices/+/up'
TOPIC_JOIN = 'v3/+/devices/+/join'
TOPIC_ACK = 'v3/+/devices/+/down/acks'

SUBSCRIBE_LIST = [TOPIC_UPLINK, TOPIC_JOIN, TOPIC_ACK]


def on_connect(client, userdata, flags, rc):
    # pylint: disable=W0613
    """
    The callback for when the client receives a CONNACK response from the
    server.
    """
    for topic in SUBSCRIBE_LIST:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    # pylint: disable=W0613
    """
    The callback for when a PUBLISH message is received from the server.
    """
    topic = msg.topic
    data = json.loads(msg.payload)
    if re.search("up", topic):
        userdata.msg.append(data)
    elif re.search("down", topic):
        userdata.ack = True


class TTNClient:
    def __init__(self):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        self.mqtt = client
        self.msg = []
        self.ack = False

    def __enter__(self):
        self.mqtt.user_data_set(self)
        self.mqtt.tls_set()
        try:
            password = get_required_envvar("TTN_DL_KEY")
        except RuntimeError:
            # Deprecated, keep old name as long as RIOT-OS/RIOT release
            # test github action is configured to use the old name
            password = get_required_envvar("LORAWAN_DL_KEY")
        self.mqtt.username_pw_set(APP_ID, password=password)
        self.mqtt.connect(TTN_MQTT_SERVER, 8883, 60)
        self.mqtt.loop_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mqtt.loop_stop()

    def publish_to_dev(self, dev_id, **kwargs):
        self.mqtt.publish(f"{APP_ID}/devices/{dev_id}/down", json.dumps(kwargs))

    def pop_uplink_payload(self):
        try:
            base64_payload = self.msg.pop()["uplink_message"]["frm_payload"]
            return base64.b64decode(base64_payload).decode('utf-8')
        except IndexError as err:
            raise RuntimeError("Uplink queue empty") from err

    def downlink_ack_received(self):
        return self.ack
