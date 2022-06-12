import asyncio
import websockets
import time
import json

async def test_client():
    uri = "ws://fastapi-websocket-server:8000/ws"
    async with websockets.connect(uri) as websocket:
        first_data = await websocket.recv()
        first_data = json.loads(first_data)
        send_data = create_message(first_data)

        while True:
            json_data = json.dumps(send_data).encode()
            await websocket.send(json_data)
            print(await websocket.recv())
            time.sleep(1)

def create_message(first_data):
    send_data = {
    "connection-message":False,
    "id":first_data["id"],
    "position-x":0.0,
    "position-y":0.0,
    "position-z":0.0,
    "rotation-x":0.0,
    "rotation-y":0.0,
    "rotation-z":0.0
    }

    return send_data

asyncio.run(test_client())