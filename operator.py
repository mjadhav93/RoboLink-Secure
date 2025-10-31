import asyncio, json, os, hmac, hashlib, ssl, time, statistics, csv, pathlib
import websockets

# Config
SECRET = os.getenv("WS_SHARED_SECRET", "supersecret")
OID = os.getenv("OP_ID", "ai-operator")
RID = os.getenv("ROBOT_ID", "robot-001")
WSS_URL = os.getenv("WSS_URL", "wss://localhost:8765")
RTT_LOG = pathlib.Path("rtt.csv")

def token(role, ident):
    return hmac.new(SECRET.encode(), f"{role}|{ident}".encode(), hashlib.sha256).hexdigest()

async def operator():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # trusting self-signed locally

    rtts = []

    async with websockets.connect(WSS_URL, ssl=ctx) as ws:
        # Auth
        await ws.send(json.dumps({"type":"auth","role":"operator","id":OID,"token":token("operator",OID)}))

        async def pinger():
            while True:
                ts = int(time.time()*1000)
                await ws.send(json.dumps({"type":"ping","to":RID,"ts":ts}))
                await asyncio.sleep(1.0)

        async def rx():
            async for msg in ws:
                obj = json.loads(msg)

                if obj.get("type") == "pong":
                    rtt = int(time.time()*1000) - int(obj["ts"])
                    rtts.append(rtt)
                    # append to CSV
                    with RTT_LOG.open("a", newline="") as f:
                        csv.writer(f).writerow([int(time.time()*1000), rtt])
                    # rolling stats every 5 samples
                    if len(rtts) % 5 == 0:
                        wnd = rtts[-50:] if len(rtts) >= 50 else rtts
                        med = statistics.median(wnd)
                        p95 = sorted(wnd)[int(0.95*len(wnd))-1]
                        print(f"RTT ms: last={rtt} med≈{med} p95≈{p95} n={len(rtts)}")

                elif obj.get("type") == "chat":
                    print(f"[robot] {obj.get('msg')}")

                elif obj.get("type") == "telemetry":
                    # Uncomment to display telemetry stream:
                    # print("telemetry:", obj)
                    pass

        async def console():
            print("Type:  drive 0.2 0.1   or   chat hello")
            loop = asyncio.get_running_loop()
            while True:
                line = await loop.run_in_executor(None, input, "> ")
                parts = line.strip().split()
                if not parts:
                    continue

                if parts[0] == "drive" and len(parts) == 3:
                    try:
                        v, w = float(parts[1]), float(parts[2])
                    except ValueError:
                        print("Usage: drive <v> <w>  (floats)")
                        continue
                    await ws.send(json.dumps({
                        "type":"cmd",
                        "to":RID,
                        "ts": int(time.time()*1000),   # freshness for replay resistance
                        "cmd":"drive",
                        "args":{"v":v,"w":w}
                    }))

                elif parts[0] == "chat":
                    msg = " ".join(parts[1:]) if len(parts) > 1 else ""
                    await ws.send(json.dumps({"type":"chat","to":RID,"msg":msg}))

                else:
                    print("Unknown. Try:  drive 0.2 0.1   |   chat hello")

        await asyncio.gather(pinger(), rx(), console())

if __name__ == "__main__":
    asyncio.run(operator())
