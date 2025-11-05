from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_users[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_users:
            del self.active_users[user_id]

    async def send(self, user_id: int, message: str):
        if user_id in self.active_users:
            await self.active_users[user_id].send_text(message)

manager = ConnectionManager()
