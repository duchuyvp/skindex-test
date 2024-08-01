from core.unit_of_work import UnitOfWork
from chat_service.domains import models
from core import abstract


def get_chat_history(room_id: str, uow: UnitOfWork):

    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        return uow.repo.get(models.Message, room_id=room_id)


def get_message(message_id: str, uow: UnitOfWork):

    with uow:
        assert isinstance(uow.repo, abstract.Repository)
        return uow.repo.get(models.Message, message_id=message_id)[0]
