import json
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

BROKER_HOST = os.environ.get("MQTT_HOST", "localhost")
_is_cloud = BROKER_HOST != "localhost"
BROKER_PORT = int(os.environ.get("MQTT_PORT", 8883 if _is_cloud else 1883))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASS = os.environ.get("MQTT_PASS")
WLED_TOPIC = "wled/lamp/api"

_client = mqtt.Client()

if MQTT_USER:
    _client.username_pw_set(MQTT_USER, MQTT_PASS)
if _is_cloud:
    _client.tls_set()

_client.connect(BROKER_HOST, BROKER_PORT)
_client.loop_start()


def send_color(rgb: tuple[int, int, int]) -> None:
    """Publish a solid color to WLED. rgb is a (r, g, b) tuple, each 0–255."""
    payload = json.dumps({"seg": [{"col": [list(rgb)]}]})
    _client.publish(WLED_TOPIC, payload)


def send_brightness(value: int) -> None:
    """Publish brightness to WLED. value is 0–255."""
    value = max(0, min(255, int(value)))
    payload = json.dumps({"bri": value})
    _client.publish(WLED_TOPIC, payload)


# Convenience color constants
COLOR_ORANGE = (255, 120, 0)
COLOR_GREEN = (0, 200, 50)
