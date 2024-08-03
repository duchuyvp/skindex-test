from fastapi import WebSocket

from chat_service.services import views

import redis
import asyncio
import json
import utils

config_path = utils.get_config_path()
config = utils.load_config(config_path)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.room_listeners: dict[str, asyncio.Task] = {}
        self.redis = redis.Redis(
            host=config["redis"]["host"],
            port=config["redis"]["port"],
            db=config["redis"]["db"],
        )

    async def connect(self, websocket: WebSocket, room_id: str):
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_listeners[room_id] = asyncio.create_task(self.listen_to_redis(room_id))
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]

            task = self.room_listeners.pop(room_id, None)
            if task:
                task.cancel()

    async def broadcast(self, room_id: str, message: dict):
        msg_text = json.dumps(message)
        await asyncio.to_thread(self.redis.publish, room_id, msg_text)
        print(f"room {room_id} sent {message["message"]}")

    async def listen_to_redis(self, room_id: str):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(room_id)
        try:
            while True:
                message = await asyncio.to_thread(
                    pubsub.get_message, ignore_subscribe_messages=True, timeout=1
                )
                if message:
                    msg_data = json.loads(message["data"])
                    print(f"room {room_id} got {msg_data["message"]}")
                    if room_id in self.active_connections:
                        for connection in self.active_connections[room_id]:
                            await connection.send_json(msg_data)
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pubsub.unsubscribe(room_id)
            pubsub.close()
            print(f"room {room_id} listener stopped")
