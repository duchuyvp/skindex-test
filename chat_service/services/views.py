from core.unit_of_work import UnitOfWork
from chat_service.domains import models
from core import abstract
import fastapi


def get_chat_history(room_id: str, password: str, uow: UnitOfWork):
    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        rooms = uow.repo.get(models.Room, id=room_id)
        if not rooms:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )
        room = rooms[0]  # type: models.Room
        if room.password and room.password != password:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password for the room",
            )
        return room.messages


def find_room(room_id: str, password: str, uow: UnitOfWork):
    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        rooms = uow.repo.get(models.Room, id=room_id, password=password)
        if not rooms:
            raise fastapi.WebSocketException(
                code=fastapi.status.WS_1000_NORMAL_CLOSURE,
                reason="Room not found or invalid password",
            )


def get_message(message_id: str, uow: UnitOfWork):

    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        return uow.repo.get(models.Message, message_id=message_id)[0]


def get_room(message_id: str, uow: UnitOfWork):

    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        return uow.repo.get(models.Room, message_id=message_id)[0]
