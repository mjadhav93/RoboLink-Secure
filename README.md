# RoboLink-Secure
Encrypted WebSocket communication framework for ESP32 robots and AI controllers — featuring TLS security, HMAC auth, and real-time telemetry exchange.


# Secure, Low-Latency ESP32 ↔ AI Controller Communication System

### 🧠 Overview
This project demonstrates a **secure, low-latency, bidirectional communication system** designed for an ESP32-based robot node interacting with a central AI controller.

Due to lack of hardware access, the ESP32 node is **simulated in Python** using the exact same protocol logic that would run on the embedded device.  
The design ensures **confidentiality, integrity, and authentication** using WebSockets over TLS and an HMAC-based token system.

---

### ⚙️ Features
- **WebSockets over TLS (WSS):** Provides encrypted, bidirectional communication.
- **HMAC-SHA256 Authentication:** Lightweight identity validation for devices.
- **Telemetry, Commands, and Chat:** JSON-based message protocol.
- **Low-Latency:** Achieves ~2–3 ms RTT on local tests.
- **ESP32 Ready:** Designed for direct porting to ESP-IDF (C).

---

### 📁 Project Structure
esp32-ws-robot/
├── certs/ # contains self-signed TLS certificates
│ ├── server.crt
│ └── server.key
├── mock_robot.py # simulated ESP32 robot node
├── operator.py # AI controller / operator interface
├── server.py # secure WebSocket server
└── README.md



### 🚀 How to Run Locally

1. **Setup environment**
   ```bash
   cd esp32-ws-robot
   python3 -m venv .venv
   source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
   pip install websockets==12.0


2. **Start the secure server**
export WS_SHARED_SECRET=supersecret
python server.py
# Expected output: 🔒 WSS server on wss://localhost:8765

3. **Start the simulated robot**
source .venv/bin/activate
export WS_SHARED_SECRET=supersecret
python mock_robot.py
# Expected: ✅ robot authenticated + telemetry logs

4. **Start the operator (AI controller)**
source .venv/bin/activate
export WS_SHARED_SECRET=supersecret
python operator.py

Type chat hello robot
Type drive 0.2 0.1
Observe RTT metrics and robot responses.

**Results**

Latency: ~2–3 ms RTT on local network
Telemetry: 10 Hz (~1 kB/s bandwidth)
Security: TLS encryption + HMAC auth + timestamp freshness


**Next Steps**

1. Implement the same logic in ESP-IDF C using:
2. esp_websocket_client for TLS WebSockets
3. mbedTLS for HMAC-SHA256
4. Lightweight JSON formatting via snprintf
5. Test on actual ESP32 hardware with the same WSS server.
