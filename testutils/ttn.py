import os
import re
import json

import paho.mqtt.client as mqtt
from testutils.pytest import get_required_envvar

APP_ID = os.environ.get("TTN_APP_ID", "11-lorawan")
DEVICE_ID = os.environ.get("TTN_DEV_ID", "riot_lorawan_1")
DEVICE_ID_ABP = os.environ.get("TTN_DEV_ID_ABP", "riot_lorawan_1_abp")
DEVEUI = os.environ.get("LORAWAN_DEV_EUI", "009E40529364FBE6")
APPEUI = os.environ.get("LORAWAN_APP_EUI", "70B3D57ED003B26A")
DEVADDR = os.environ.get("LORAWAN_DEV_ADDR", "26011EB0")


def on_connect(client, userdata, flags, rc):
    # pylint: disable=W0613
    """
    The callback for when the client receives a CONNACK response from the
    server.
    """
    client.subscribe('+/devices/+/up')
    client.subscribe('+/devices/+/events/activations')
    client.subscribe("+/devices/+/events/down/acks")


def on_message(client, userdata, msg):
    # pylint: disable=W0613
    """
    The callback for when a PUBLISH message is received from the server.
    """
    topic = msg.topic
    data = json.loads(msg.payload)
    if re.search("up", topic):
        userdata["msg"] = data
    else:
        userdata["ack"] = data


class TTNClient:
    def __init__(self):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        self.mqtt = client
        self.userdata = {}

    def __enter__(self):
        self.mqtt.user_data_set(self.userdata)
        self.mqtt.tls_set()
        password = get_required_envvar("LORAWAN_DL_KEY")
        self.mqtt.username_pw_set(APP_ID, password=password)
        self.mqtt.connect('eu.thethings.network', 8883, 60)
        self.mqtt.loop_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mqtt.loop_stop()

    def publish_to_dev(self, app_id, dev_id, **kwargs):
        self.mqtt.publish("{}/devices/{}/down".format(app_id, dev_id),
                            json.dumps(kwargs))
