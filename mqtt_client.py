import json
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
WLED_TOPIC = "wled/lamp/api"

_client = mqtt.Client()
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


# Convenience color constants used by classroom.py
COLOR_ORANGE = (255, 120, 0)
COLOR_GREEN = (0, 200, 50)
