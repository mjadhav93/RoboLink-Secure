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
