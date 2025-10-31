import asyncio, json, os, hmac, hashlib, ssl
import websockets

SECRET = os.getenv("WS_SHARED_SECRET", "supersecret")
CERT = "certs/server.crt"
KEY  = "certs/server.key"

robots = {}     
operators = {}  

def make_token(role, ident):
    msg = f"{role}|{ident}".encode()
    return hmac.new(SECRET.encode(), msg, hashlib.sha256).hexdigest()

async def auth(ws):
    msg = await asyncio.wait_for(ws.recv(), timeout=5)
    obj = json.loads(msg)
    assert obj["type"] == "auth"
    role = obj["role"]
    ident = obj["id"]
    token = obj["token"]
    if token != make_token(role, ident):
        raise websockets.exceptions.SecurityError("bad token")
    return role, ident

async def handler(ws):
    role, ident = await auth(ws)
    if role == "robot":
        robots[ident] = ws
        print(f"🤖 robot {ident} connected")
    else:
        operators[ident] = ws
        print(f"👤 operator {ident} connected")

    try:
        async for msg in ws:
            obj = json.loads(msg)
            t = obj.get("type")
            if t == "cmd" and role == "operator":
                rid = obj["to"]
                if rid in robots:
                    await robots[rid].send(json.dumps(obj))
            elif t == "ping" and role == "operator":
                rid = obj["to"]
                if rid in robots:
                    await robots[rid].send(json.dumps(obj))
            elif t == "telemetry" and role == "robot":
                payload = json.dumps(obj)
                await asyncio.gather(*(op.send(payload) for op in operators.values()),
                                     return_exceptions=True)
            elif t == "chat":
                dest = obj.get("to")
                payload = json.dumps(obj)
                if role == "operator" and dest in robots:
                    await robots[dest].send(payload)
                elif role == "robot":
                    await asyncio.gather(*(op.send(payload) for op in operators.values()),
                                         return_exceptions=True)
            elif t == "pong" and role == "robot":
                payload = json.dumps(obj)
                await asyncio.gather(*(op.send(payload) for op in operators.values()),
                                     return_exceptions=True)
    finally:
        if role == "robot":
            robots.pop(ident, None)
            print(f"❌ robot {ident} disconnected")
        else:
            operators.pop(ident, None)
            print(f"❌ operator {ident} disconnected")

async def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, KEY)
    async with websockets.serve(handler, "localhost", 8765, ssl=ctx, ping_interval=30):
        print("🔒 WSS server on wss://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
