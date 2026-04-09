import eventlet
eventlet.monkey_patch()

import os
import threading
import time

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

import mqtt_client
from classroom import check_assignments

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

_current_status = {"color": "orange", "text": "Pending assignments"}
_mode = "auto"  # "auto" = classroom controls lamp color; "manual" = slider controls lamp color


def _do_poll():
    """Run one classroom check and update state. Returns the color."""
    color = check_assignments()
    text = "All done" if color == "green" else "Pending assignments"
    changed = color != _current_status["color"]
    _current_status["color"] = color
    _current_status["text"] = text
    if changed:
        if _mode == "auto":
            rgb = mqtt_client.COLOR_GREEN if color == "green" else mqtt_client.COLOR_ORANGE
            mqtt_client.send_color(rgb)
        socketio.emit("status_update", _current_status)
    print(f"[classroom poll] {color} (changed={changed})")
    return color


def _poll_classroom():
    """Background thread: checks Google Classroom every 5 seconds."""
    while True:
        try:
            _do_poll()
        except Exception as e:
            print(f"[classroom poll error] {e}")
        time.sleep(5)


# Start background polling — runs under both direct execution and gunicorn
_poll_thread = threading.Thread(target=_poll_classroom, daemon=True)
_poll_thread.start()


# ── HTTP routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    return jsonify({**_current_status, "mode": _mode})


# ── WebSocket events ─────────────────────────────────────────────────────────

@socketio.on("brightness_change")
def on_brightness(data):
    # Frontend sends 0–100; WLED expects 0–255
    raw = int(data.get("value", 100))
    mqtt_client.send_brightness(round(raw * 255 / 100))


@socketio.on("mode_change")
def on_mode_change(data):
    global _mode
    _mode = "auto" if data.get("mode") == "auto" else "manual"
    if _mode == "auto":
        rgb = mqtt_client.COLOR_GREEN if _current_status["color"] == "green" else mqtt_client.COLOR_ORANGE
        mqtt_client.send_color(rgb)


@socketio.on("color_temp_change")
def on_color_temp(data):
    """
    Slider 0 = warm (2700 K orange-white), 100 = cool (6500 K blue-white).
    Only applies in manual mode — in auto mode the classroom status owns the color.
    """
    if _mode != "manual":
        return
    v = max(0, min(100, int(data.get("value", 50)))) / 100
    warm = (255, 147, 41)
    cool = (220, 235, 255)
    rgb = tuple(round(warm[i] + (cool[i] - warm[i]) * v) for i in range(3))
    mqtt_client.send_color(rgb)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=False)
