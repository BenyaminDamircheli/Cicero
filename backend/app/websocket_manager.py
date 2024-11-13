from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    """
    Manages WebSocket connections.
    """
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {} # dictionary of client ids and their websocket connections

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        print(f"Client {client_id} connected")
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        print(f"Client {client_id} disconnected")
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")

manager = ConnectionManager()