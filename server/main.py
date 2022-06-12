import json
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time

# json構造
# {
#     "connection-message":True,
#     "id":0,
#     "position-x":0.0,
#     "position-y":0.0,
#     "position-z":0.0,
#     "rotation-x":0.0,
#     "rotation-y":0.0,
#     "rotation-z":0.0
# }

# FaskAPIオブジェクト作成
app = FastAPI()
MAX_CONNECTION = 10

# 接続管理用オブジェクト
class ConnenctionManager:
    def __init__(self) -> None:
        self.active_connections : Dict = {}
        self.object_ids : Dict = {}
    
    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        # 既に10件の接続があれば拒否
        if len(self.object_ids.values()) == MAX_CONNECTION:
            await websocket.close()

        # websocket接続キーをキーとする
        key = websocket.headers.get('sec-websocket-key')
        self.active_connections[key] = websocket

        # 接続時にidを降る
        for i in range(MAX_CONNECTION):
            if i not in self.object_ids.values():
                self.object_ids[key] = i
                break
    
        send_data = {
            "connection-message":True,
            "id":self.object_ids[key]
        }
        # id送信
        # time.sleep(1)
        await self.send_personal_json_message(send_data,websocket)

    def disconnect(self, websocket:WebSocket):
        key = websocket.headers.get('sec-websocket-key')
        del self.active_connections[key]
        del self.object_ids[key]
    
    async def send_personal_json_message(self, json_message:Dict, websocket:WebSocket):
        await websocket.send_json(json_message)

    async def broadcast(self, json_message:Dict):
        for connection in self.active_connections.values():
            await connection.send_json(json_message)

    async def broadcast_excluding_sender(self, json_message:Dict, websocket:WebSocket):
        for connection in self.active_connections.values():
            if connection != websocket:
                await connection.send_json(json_message)

manager = ConnenctionManager()

# WebSockets用のエンドポイント
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            data = json.loads(data)
            print(data)
            # await manager.send_personal_json_message({"responce":"true"}, websocket)
            await manager.broadcast_excluding_sender(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)