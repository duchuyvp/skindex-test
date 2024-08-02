import fastapi

from chat_service.domains import commands
from chat_service.entrypoints.rest import websocket
from chat_service.bootstrap import bootstrap
from chat_service.services import views

router = fastapi.APIRouter()
manager = websocket.ConnectionManager()
bus = bootstrap()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: fastapi.WebSocket, room_id: str, password: str):
    views.find_room(room_id, password, bus.uow)
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            cmd = commands.SendMessage(
                room_id=room_id,
                message=data,
                image=None,
                username="Anonymous",
            )
            bus.handle(cmd)
            message = views.get_message(cmd._id, bus.uow)
            await manager.broadcast(room_id, message.json)
    except fastapi.WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
