# uvicorn main:app --reload --host 0.0.0.0 --port 8000
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time

# json構造
# {
#     "connection_message":True,
#     "disconnection_message":False,
#     "id":0,
#     "position_x":0.0,
#     "position_y":0.0,
#     "position_z":0.0,
#     "rotation_x":0.0,
#     "rotation_y":0.0,
#     "rotation_z":0.0
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
        # # 既に10件の接続があれば拒否
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
            "connection_message":True,
            "disconnection_message":False,
            "id":self.object_ids[key],
            "position_x":0.0,
            "position_y":0.0,
            "position_z":0.0,
            "rotation_x":0.0,
            "rotation_y":0.0,
            "rotation_z":0.0
        }
        # id送信
        # todo:瞬時に返却するとunityのawake終了前に帰る可能性があるので1s止める
        time.sleep(1)
        await self.send_personal_json_message(send_data,websocket)

        print("connection"+str(self.object_ids[key]))

    async def disconnect(self, websocket:WebSocket):
        key = websocket.headers.get('sec-websocket-key')

        send_data = {
            "connection_message":False,
            "disconnection_message":True,
            "id":self.object_ids[key],
            "position_x":0.0,
            "position_y":0.0,
            "position_z":0.0,
            "rotation_x":0.0,
            "rotation_y":0.0,
            "rotation_z":0.0
        }
        await self.broadcast_excluding_sender(send_data, websocket)
        print("disconnection"+str(self.object_ids[key]))

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
    print("connect!")
    await manager.connect(websocket)
    try:
        while True:
            # C#側のアクセス
            data = await websocket.receive_json()

            # python側のデバッグ
            # data = await websocket.receive_bytes()
            # data = json.loads(data)

            # print(data)
            await manager.broadcast_excluding_sender(data, websocket)
    except WebSocketDisconnect:
         await manager.disconnect(websocket)
