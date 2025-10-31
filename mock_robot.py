import asyncio, json, os, hmac, hashlib, ssl, time, random
import websockets

# Config
SECRET = os.getenv("WS_SHARED_SECRET", "supersecret")
RID = os.getenv("ROBOT_ID", "robot-001")
WSS_URL = os.getenv("WSS_URL", "wss://localhost:8765")
CMD_MAX_AGE_MS = int(os.getenv("CMD_MAX_AGE_MS", "2000"))  # drop stale cmds (>2s)

def token(role, ident):
    return hmac.new(SECRET.encode(), f"{role}|{ident}".encode(), hashlib.sha256).hexdigest()

async def robot():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # trusting self-signed locally

    async with websockets.connect(WSS_URL, ssl=ctx) as ws:
        # Auth
        await ws.send(json.dumps({"type":"auth","role":"robot","id":RID,"token":token("robot",RID)}))
        print("✅ robot authenticated")

        async def telemetry_loop():
            counter = 0
            while True:
                now = int(time.time()*1000)
                bat = round(3.8 + random.random()*0.3, 2)
                temp = round(35.5 + random.random()*2.0, 1)
                await ws.send(json.dumps({
                    "type":"telemetry","id":RID,"ts":now,"bat":bat,"temp":temp
                }))
                counter += 1
                if counter % 10 == 0:  # ~1/sec at 10 Hz
                    print(f"📡 telemetry sent (ts={now}, bat={bat}, temp={temp})")
                await asyncio.sleep(0.1)  # 10 Hz

        async def rx_loop():
            async for msg in ws:
                obj = json.loads(msg)

                if obj.get("type") == "ping":
                    # immediate pong with same ts for RTT measurement
                    await ws.send(json.dumps({"type":"pong","id":RID,"ts":obj["ts"]}))

                elif obj.get("type") == "cmd":
                    # drop stale commands (simple replay/freshness defense)
                    now_ms = int(time.time()*1000)
                    ts = int(obj.get("ts", 0))
                    if now_ms - ts > CMD_MAX_AGE_MS:
                        print(f"⚠️ stale cmd dropped (age={now_ms - ts} ms): {obj}")
                        continue

                    print(f"🛠️ cmd received: {obj}")
                    # act quickly; here we just ACK via chat
                    await ws.send(json.dumps({
                        "type":"chat","id":RID,"msg":f"ack {obj['cmd']} {obj.get('args',{})}"
                    }))

                elif obj.get("type") == "chat":
                    print(f"💬 chat from operator: {obj.get('msg')}")
                    await ws.send(json.dumps({
                        "type":"chat","id":RID,"msg":"echo: "+obj.get('msg','')
                    }))

        await asyncio.gather(telemetry_loop(), rx_loop())

if __name__ == "__main__":
    asyncio.run(robot())
