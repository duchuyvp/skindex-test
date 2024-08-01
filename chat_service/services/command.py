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


COMMAND_HANDLERS: dict[type[core.Command], Callable[..., None]] = {
    commands.SendMessage: send_message,
}
