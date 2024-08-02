import os
import fastapi

from chat_service.bootstrap import bootstrap
from chat_service.services import views
from chat_service.entrypoints import schemas

router = fastapi.APIRouter()
bus = bootstrap()


@router.get("/chats")
async def get_chats(room_id: str, password: str) -> list[schemas.MessageResponse]:
    history = views.get_chat_history(room_id, password, bus.uow)
    return history
