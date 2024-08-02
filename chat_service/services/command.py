from typing import Any, Callable
from chat_service.domains import models
from chat_service.domains import commands
import core
from core import abstract


def send_message(command: commands.SendMessage, uow: core.UnitOfWork):
    """
    This function sends a message.
    """
    with uow:
        message = models.Message(
            message_id=command._id,
            room_id=command.room_id,
            message=command.message,
            image=command.image,
            username=command.username,
        )

        assert isinstance(uow.repo, abstract.Repository)
        uow.repo.add(message)
        uow.commit()


def create_room(command: commands.CreateRoom, uow: core.UnitOfWork):
    """
    This function creates a room.
    """
    with uow:
        room = models.Room(
            message_id=command._id,
            password=command.password,
        )

        assert isinstance(uow.repo, abstract.Repository)
        uow.repo.add(room)
        uow.commit()


COMMAND_HANDLERS: dict[type[core.Command], Callable[..., None]] = {
    commands.SendMessage: send_message,
    commands.CreateRoom: create_room,
}
