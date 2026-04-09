# IoT Smart Lamp

An ESP32-C3 lamp that turns **orange** when you have pending Google Classroom assignments and **green** when everything is submitted. Includes a web app for manual brightness and color temperature control.

## Stack

| Layer | Technology |
|---|---|
| Hardware | ESP32-C3, WS2812B LED strip |
| Firmware | WLED |
| Broker | Mosquitto MQTT |
| Backend | Python, Flask-SocketIO |
| Frontend | HTML, CSS, JavaScript (WebSocket) |
| Integration | Google Classroom API (OAuth2) |

## Project Structure

```
iot_lamp/
├── app.py               # Flask server, WebSocket events, classroom polling
├── classroom.py         # Google Classroom API + OAuth2
├── mqtt_client.py       # Publishes color/brightness commands to WLED via MQTT
├── requirements.txt
├── credentials.json     # Google OAuth client credentials (not committed)
├── token.json           # Saved OAuth token, auto-generated on first login (not committed)
├── templates/
│   └── index.html       # Web UI
└── static/
    ├── app.js           # WebSocket client, slider handlers
    └── style.css
```

## Setup

### 1. Hardware & WLED

1. Wire the WS2812B strip to the ESP32-C3 — power the strip directly from a 5V supply, not the ESP32 pin. Use a 300–500Ω resistor on the data line.
2. Flash WLED from [install.wled.me](https://install.wled.me).
3. On first boot connect to the `WLED-AP` hotspot, enter your WiFi credentials at `192.168.4.1`.
4. In the WLED UI go to **Config → LED Preferences** and set the LED pin and count.

### 2. Mosquitto MQTT Broker

Install and start Mosquitto on Windows:

```
Download from mosquitto.org/download, run the installer.
Open Services (Win+R → services.msc) and confirm Mosquitto is running.
```

Allow port 1883 through the firewall (run as admin):

```
netsh advfirewall firewall add rule name="Mosquitto MQTT" dir=in action=allow protocol=TCP localport=1883
```

### 3. WLED MQTT Configuration

In the WLED web UI go to **Config → Sync Interfaces → MQTT**:

| Field | Value |
|---|---|
| Enable MQTT | checked |
| Broker | your PC's local IP (e.g. `192.168.0.101`) |
| Port | `1883` |
| Device topic | `lamp` |

Save — WLED will now listen on `wled/lamp/api`.

### 4. Google Cloud Credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project.
2. Enable the **Google Classroom API**.
3. Configure the OAuth consent screen (External, add your Google account as a test user).
4. Create an **OAuth 2.0 Client ID** — type: Desktop app.
5. Download the JSON file, rename it to `credentials.json`, place it in the project root.

### 5. Python Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

On first run a browser will open for Google login. After approving, `token.json` is saved and logins are automatic from then on.

Open `http://127.0.0.1:5000` in a browser.

## How It Works

- A background thread polls Google Classroom every 5 seconds.
- If any assignment is not `TURNED_IN` or `RETURNED`, the lamp turns **orange**.
- When all assignments are submitted, the lamp turns **green**.
- The web app has a **brightness slider** (always active) and a **color temperature slider**.
- A toggle switches between **Auto mode** (classroom controls lamp color) and **Manual mode** (color temperature slider controls lamp color). The status badge always reflects the real assignment state regardless of mode.

## Common Issues

| Problem | Fix |
|---|---|
| LEDs don't light up | Check GPIO pin in WLED LED Preferences |
| ESP32 can't reach MQTT broker | Check firewall on port 1883, use PC's local IP not `localhost` in WLED |
| Google login loop / token error | Delete `token.json` and re-run `python app.py` |
| Status badge stuck on orange | Check terminal for `[classroom poll error]` messages |
| Lamp doesn't respond to sliders | Confirm WLED MQTT is enabled and device topic is `lamp` |
