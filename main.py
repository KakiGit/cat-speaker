#!/usr/bin/env python

import paho.mqtt.client as mqtt
import json
import os
from pydub import AudioSegment
from pydub.playback import play
import multiprocessing as mp
import logging
import time

logging.basicConfig(filename="cat-speaker.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

with open("configuration.json") as f:
    data = json.load(f)
TOPIC_SOUND_MAP = {}
for topic in data:
    TOPIC_SOUND_MAP[topic] = {}
    for action in data[topic]["actions"]:
        TOPIC_SOUND_MAP[topic][action] = AudioSegment.from_mp3(os.path.expanduser(data[topic]["actions"][action]))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in TOPIC_SOUND_MAP:
        client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    if topic not in TOPIC_SOUND_MAP:
        return
    logging.info(data[topic]["message"])
    payload = json.loads(msg.payload)
    if "action" in payload:
        action = payload["action"]
        if payload["action"] in TOPIC_SOUND_MAP[topic]:
            mp.Process(target=play, args=(TOPIC_SOUND_MAP[topic][action],)).start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
try:
    client.loop_forever()
except:
    pass
finally:
    ea_p.terminate()
