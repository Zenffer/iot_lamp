import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WLED_IP = os.environ.get("WLED_IP", "")
_BASE_URL = f"http://{WLED_IP}/json/state"

COLOR_ORANGE = (255, 120, 0)
COLOR_GREEN = (0, 200, 50)


def _post(payload: dict) -> None:
    if not WLED_IP:
        print("[wled] WLED_IP not set — skipping command")
        return
    try:
        requests.post(_BASE_URL, json=payload, timeout=3)
    except Exception as e:
        print(f"[wled] HTTP error: {e}")


def send_color(rgb: tuple[int, int, int]) -> None:
    _post({"seg": [{"col": [list(rgb)]}]})


def send_brightness(value: int) -> None:
    value = max(0, min(255, int(value)))
    _post({"bri": value})
