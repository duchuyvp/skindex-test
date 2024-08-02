import os
import fastapi

from chat_service.bootstrap import bootstrap
from chat_service.services import views
from chat_service.domains import commands
from chat_service.entrypoints import schemas

router = fastapi.APIRouter()
bus = bootstrap()


@router.post("/rooms", status_code=fastapi.status.HTTP_201_CREATED)
async def create_room(password: str = fastapi.Body(embed=True)) -> schemas.RoomResponse:
    cmd = commands.CreateRoom(password=password)
    bus.handle(cmd)

    room = views.get_room(cmd._id, bus.uow)
    return room
